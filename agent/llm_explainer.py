# agent/llm_explainer.py

from groq import Groq
import os

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def explain_anomaly(record):
    """
    Generates an explanation for a suspicious login record using Groq AI.
    """

    prompt = f"""
You are a cybersecurity expert LLM agent.
Analyze the following login record and generate a clear, short explanation of why it might be an anomaly:

Timestamp: {record['timestamp']}
User ID: {record['user_id']}
IP Address: {record['ip_address']}
Geo Location: {record['geo_location']}
Device: {record['device']}
Attempt Count: {record['attempt_count']}
Login Success: {record['login_success']}

List clear reasons based on unusual patterns, suspicious locations, failed attempts, or new device usage.
End with a recommendation if needed.
"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful cybersecurity LLM explainer."},
                {"role": "user", "content": prompt}
            ]
        )
        explanation = response.choices[0].message.content.strip()
        return explanation
    except Exception as e:
        return f"⚠️ LLM explanation could not be generated. Reason: {e}"
