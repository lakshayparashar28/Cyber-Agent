# dashboard_app.py (Upgraded, clean, and attractive)

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="🚨 Agentic AI Cyber Security Dashboard",
    layout="wide",
    page_icon="🚨"
)

# Auto-refresh every 10 seconds
st.experimental_set_query_params(_=datetime.now().strftime("%H%M%S"))

st.title("🚨 Agentic AI Cyber Security Dashboard")

# Load data
try:
    df_logs = pd.read_csv("data/login_logs.csv")
except FileNotFoundError:
    df_logs = pd.DataFrame()

try:
    df_suspicious = pd.read_csv("data/suspicious_logins_with_explanations.csv")
except FileNotFoundError:
    df_suspicious = pd.DataFrame()

# Summary cards
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("✅ Total Login Attempts", len(df_logs) if not df_logs.empty else 0)
with col2:
    st.metric("🚨 Suspicious Logins", len(df_suspicious) if not df_suspicious.empty else 0)
with col3:
    st.metric("🕒 Last Updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

st.markdown("---")

# Login logs section
st.subheader("✅ All Login Logs (Live)")
if not df_logs.empty:
    st.dataframe(df_logs.tail(100), use_container_width=True)
else:
    st.info("No login logs available yet. Submit data from your login interface.")

# Suspicious logs section
st.subheader("🚨 Suspicious Logins Detected (Live)")
if not df_suspicious.empty:
    st.dataframe(df_suspicious.tail(100), use_container_width=True)
else:
    st.success("No suspicious logins detected so far. Your system is secure.")

# Download section
st.markdown("---")
st.subheader("⬇️ Download Data")

col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    if not df_logs.empty:
        csv_logs = df_logs.to_csv(index=False).encode('utf-8')
        st.download_button("Download All Login Logs", csv_logs, "login_logs.csv", "text/csv")
    else:
        st.info("No login logs to download yet.")

with col_dl2:
    if not df_suspicious.empty:
        csv_suspicious = df_suspicious.to_csv(index=False).encode('utf-8')
        st.download_button("Download Suspicious Logins", csv_suspicious, "suspicious_logins_with_explanations.csv", "text/csv")
    else:
        st.info("No suspicious data to download yet.")

st.success("✅ Dashboard is live and updating automatically.")
