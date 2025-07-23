# dashboard_app.py (cleaned and final)

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Agentic AI Cyber Security Dashboard", layout="wide")

st.title("📊 Agentic AI Cyber Security Dashboard")
st.write("This dashboard displays **stored login data** and **detected suspicious logins** in real time.")

# Display stored login data
st.header("✅ All Login Logs")
try:
    df_logs = pd.read_csv("data/login_logs.csv")
    st.dataframe(df_logs, use_container_width=True)
except FileNotFoundError:
    st.warning("No login_logs.csv found yet. Please add data using the login interface.")

# Display suspicious logins with explanations
st.header("🚨 Suspicious Logins Detected")
try:
    df_suspicious = pd.read_csv("data/suspicious_logins_with_explanations.csv")
    st.dataframe(df_suspicious, use_container_width=True)
except FileNotFoundError:
    st.warning("No suspicious_logins_with_explanations.csv found yet. No suspicious logins detected so far.")

# Optional: Download buttons
st.header("⬇️ Download Data")
col1, col2 = st.columns(2)

with col1:
    if "df_logs" in locals():
        csv = df_logs.to_csv(index=False).encode('utf-8')
        st.download_button("Download login_logs.csv", csv, "login_logs.csv", "text/csv")

with col2:
    if "df_suspicious" in locals():
        csv_s = df_suspicious.to_csv(index=False).encode('utf-8')
        st.download_button("Download suspicious_logins_with_explanations.csv", csv_s, "suspicious_logins_with_explanations.csv", "text/csv")

st.success("Dashboard loaded successfully.")
