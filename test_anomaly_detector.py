import pandas as pd
import joblib

def test_anomaly_detector(file_path="data/login_logs.csv", sample_size=2000):
    # Load trained model and encoders
    model = joblib.load("models/anomaly_detector.pkl")
    le_user = joblib.load("models/le_user.pkl")
    le_geo = joblib.load("models/le_geo.pkl")
    le_device = joblib.load("models/le_device.pkl")
    
    # Load new data
    df = pd.read_csv(file_path).sample(sample_size, random_state=42).reset_index(drop=True)

    # Encode categorical variables using previously fitted encoders
    df['user_id_enc'] = le_user.transform(df['user_id'])
    df['geo_enc'] = le_geo.transform(df['geo_location'])
    df['device_enc'] = le_device.transform(df['device'])

    # Prepare features
    X = df[['user_id_enc', 'geo_enc', 'device_enc', 'login_success', 'attempt_count']]

    # Predict anomalies
    preds = model.predict(X)  # -1 = anomaly, 1 = normal
    df['prediction'] = preds

    # Show suspicious logins
    flagged = df[df['prediction'] == -1]
    print(f"\n[✔] Total samples checked: {sample_size}")
    print(f"[✔] Suspicious logins detected: {len(flagged)}\n")

    if not flagged.empty:
        print(flagged[['timestamp', 'user_id', 'ip_address', 'geo_location', 'device', 'attempt_count', 'login_success']])
    else:
        print("[✔] No suspicious logins detected in this sample.")

if __name__ == "__main__":
    test_anomaly_detector()
