# === Updated pipeline_run.py with New User Detection ===

import pandas as pd
import joblib
import os
import logging
from sklearn.preprocessing import OrdinalEncoder
from agent.llm_explainer import explain_anomaly
from notify_telegram import send_telegram_message
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def run_pipeline(file_path="data/login_logs.csv", output_path="data/suspicious_logins_with_explanations.csv"):
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

    # Load model and encoders
    logging.info("[+] Loading model and encoders...")
    model = joblib.load("models/anomaly_detector.pkl")
    le_user = joblib.load("models/le_user.pkl")
    le_geo = joblib.load("models/le_geo.pkl")
    le_device = joblib.load("models/le_device.pkl")

    # Convert LabelEncoders to OrdinalEncoders with unknown handling
    user_encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    geo_encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    device_encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)

    user_encoder.categories_ = [le_user.classes_]
    geo_encoder.categories_ = [le_geo.classes_]
    device_encoder.categories_ = [le_device.classes_]

    logging.info(f"[+] Loading data from {file_path}...")
    df = pd.read_csv(file_path)

    df['user_id_enc'] = user_encoder.transform(df[['user_id']])
    df['geo_enc'] = geo_encoder.transform(df[['geo_location']])
    df['device_enc'] = device_encoder.transform(df[['device']])

    X = df[['user_id_enc', 'geo_enc', 'device_enc', 'login_success', 'attempt_count']]
    preds = model.predict(X)
    df['prediction'] = preds

    flagged = df[df['prediction'] == -1].copy().head(10)

    if flagged.empty:
        logging.info("[✔] No suspicious logins detected.")
    else:
        logging.info(f"[✔] {len(flagged)} suspicious logins detected.")
        
        send_telegram_message(f"🚨 Alert: {len(flagged)} suspicious logins detected (including potential new user logins). Check your dashboard.")
        logging.info("[✔] Telegram alert sent.")
        
        explanations = []

        def generate_explanation(row):
            record = {
                "timestamp": row['timestamp'],
                "user_id": row['user_id'],
                "ip_address": row['ip_address'],
                "geo_location": row['geo_location'],
                "device": row['device'],
                "attempt_count": row['attempt_count'],
                "login_success": row['login_success']
            }
            explanation = explain_anomaly(record)
            if row['user_id_enc'] == -1:
                explanation += "\n⚠️ Note: This is a NEW USER login attempt, which may be suspicious."
            return explanation

        with ThreadPoolExecutor(max_workers=1) as executor:
            futures = [executor.submit(generate_explanation, row) for idx, row in flagged.iterrows()]
            for future in futures:
                try:
                    explanation = future.result(timeout=30)
                except TimeoutError:
                    explanation = "⚠️ Explanation generation timed out."
                explanations.append(explanation)
                logging.info(f"[+] Explanation: {explanation[:100]}...")

        flagged['explanation'] = explanations

        flagged.to_csv(output_path, index=False)
        logging.info(f"[✔] Saved flagged logins with explanations to {output_path}.")

if __name__ == "__main__":
    run_pipeline()