# login_interface.py

import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from agent.llm_explainer import explain_anomaly
from notify_telegram import send_telegram_message
import os

def load_models():
    model = joblib.load("models/anomaly_detector.pkl")
    le_user = joblib.load("models/le_user.pkl")
    le_geo = joblib.load("models/le_geo.pkl")
    le_device = joblib.load("models/le_device.pkl")
    return model, le_user, le_geo, le_device

def process_uploaded_file(df_uploaded):
    st.success("✅ File uploaded successfully. Processing...")

    if os.path.exists("data/login_logs.csv"):
        df_logs = pd.read_csv("data/login_logs.csv")
    else:
        df_logs = pd.DataFrame(columns=df_uploaded.columns)

    combined = pd.concat([df_logs, df_uploaded]).drop_duplicates()
    new_entries = combined[~combined.index.isin(df_logs.index)]
    combined.to_csv("data/login_logs.csv", index=False)
    st.success(f"✅ Appended {len(new_entries)} new entries to login_logs.csv")

    model, le_user, le_geo, le_device = load_models()

    df_uploaded["user_id_enc"] = df_uploaded["user_id"].apply(lambda x: le_user.transform([x])[0] if x in le_user.classes_ else -1)
    df_uploaded["geo_enc"] = df_uploaded["geo_location"].apply(lambda x: le_geo.transform([x])[0] if x in le_geo.classes_ else -1)
    df_uploaded["device_enc"] = df_uploaded["device"].apply(lambda x: le_device.transform([x])[0] if x in le_device.classes_ else -1)

    X_uploaded = df_uploaded[["user_id_enc", "geo_enc", "device_enc", "login_success", "attempt_count"]]
    preds_uploaded = model.predict(X_uploaded)
    df_uploaded["prediction"] = preds_uploaded

    suspicious = df_uploaded[df_uploaded["prediction"] == -1].copy()
    explanations = []

    for idx, row in suspicious.iterrows():
        record = {
            "timestamp": row["timestamp"],
            "user_id": row["user_id"],
            "ip_address": row["ip_address"],
            "geo_location": row["geo_location"],
            "device": row["device"],
            "attempt_count": row["attempt_count"],
            "login_success": row["login_success"]
        }
        explanation = explain_anomaly(record)
        if row["user_id_enc"] == -1:
            explanation += "\n⚠️ Note: This is a NEW USER login attempt, which may be suspicious."
        explanations.append(explanation)
        send_telegram_message(f"🚨 Suspicious login detected for user {row['user_id']}. Check your dashboard.")

    suspicious["explanation"] = explanations

    if not suspicious.empty:
        if not os.path.exists("data/suspicious_logins_with_explanations.csv"):
            suspicious.to_csv("data/suspicious_logins_with_explanations.csv", index=False)
        else:
            suspicious.to_csv("data/suspicious_logins_with_explanations.csv", mode="a", header=False, index=False)
        st.error(f"🚨 {len(suspicious)} suspicious logins detected. Alerts sent.")
        st.dataframe(suspicious)
    else:
        st.success("✅ No suspicious logins detected in the uploaded file.")

def main():
    st.title("🚨 Agentic AI Cyber Security - Login Anomaly Checker")
    
    st.header("📂 Batch Upload for Anomaly Check")
    uploaded_file = st.file_uploader("Upload CSV file for batch login anomaly check", type=["csv"])
    if uploaded_file is not None:
        df_uploaded = pd.read_csv(uploaded_file)
        process_uploaded_file(df_uploaded)

    st.header("🖊️ Manual Login Entry for Instant Check")
    st.write("Enter login details below:")

    user_id = st.text_input("User ID")
    ip_address = st.text_input("IP Address")
    geo_location = st.text_input("Geo Location")
    device = st.text_input("Device")
    attempt_count = st.number_input("Attempt Count", min_value=0, max_value=100, value=1)
    login_success = st.selectbox("Login Success", [0, 1], format_func=lambda x: "Success" if x else "Failed")

    if st.button("Submit and Check"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = pd.DataFrame([{
            "timestamp": timestamp,
            "user_id": user_id,
            "ip_address": ip_address,
            "geo_location": geo_location,
            "device": device,
            "attempt_count": attempt_count,
            "login_success": login_success
        }])

        if not os.path.exists("data/login_logs.csv"):
            new_entry.to_csv("data/login_logs.csv", index=False)
        else:
            new_entry.to_csv("data/login_logs.csv", mode='a', header=False, index=False)

        ## st.success("✅ Login entry saved to login_logs.csv")
        model, le_user, le_geo, le_device = load_models()

        user_enc = le_user.transform([user_id])[0] if user_id in le_user.classes_ else -1
        geo_enc = le_geo.transform([geo_location])[0] if geo_location in le_geo.classes_ else -1
        device_enc = le_device.transform([device])[0] if device in le_device.classes_ else -1

        X = pd.DataFrame([{
            "user_id_enc": user_enc,
            "geo_enc": geo_enc,
            "device_enc": device_enc,
            "login_success": login_success,
            "attempt_count": attempt_count
        }])

        prediction = model.predict(X)[0]
        record = {
            "timestamp": timestamp,
            "user_id": user_id,
            "ip_address": ip_address,
            "geo_location": geo_location,
            "device": device,
            "attempt_count": attempt_count,
            "login_success": login_success
        }
        explanation = explain_anomaly(record)
        
        explanation = "🤖 *This explanation is generated by your local LLaMA model.*\n\n" + explanation

        if user_enc == -1:
            explanation += "\n⚠️ Note: This is a NEW USER login attempt, which may be suspicious."

        if prediction == -1:
            st.error("🚨 Suspicious Login Detected!")
            st.write(explanation)

            flagged_entry = new_entry.copy()
            flagged_entry["explanation"] = explanation

            if not os.path.exists("data/suspicious_logins_with_explanations.csv"):
                flagged_entry.to_csv("data/suspicious_logins_with_explanations.csv", index=False)
            else:
                flagged_entry.to_csv("data/suspicious_logins_with_explanations.csv", mode='a', header=False, index=False)

            send_telegram_message(f"🚨 Suspicious login detected for user {user_id}. Check your dashboard.")
            st.success("🚀 Telegram alert sent.")
        else:
            st.success("✅ Login is normal. No anomaly detected.")
            st.write(explanation)
            

if __name__ == "__main__":
    st.set_page_config(page_title="Agentic AI Cyber Security", page_icon="🚨")
    main()
    
st.markdown("---")
st.header("📊 View Live Dashboard")

if st.button("Check Live Dashboard"):
    dashboard_url = "https://lakshay-cyber-dashboard.streamlit.app"
    js = f"window.open('{dashboard_url}')"  # JavaScript to open in new tab
    st.markdown(f"<script>{js}</script>", unsafe_allow_html=True)
    
