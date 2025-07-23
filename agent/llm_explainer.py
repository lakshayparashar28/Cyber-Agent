import requests
import json

def explain_anomaly(record):
    prompt = f"""
You are a cybersecurity analyst AI. Explain in clear, human-readable terms why the following login event might be suspicious:

Login Event:
- Timestamp: {record['timestamp']}
- User ID: {record['user_id']}
- IP Address: {record['ip_address']}
- Geo Location: {record['geo_location']}
- Device: {record['device']}
- Attempt Count: {record['attempt_count']}
- Login Success: {record['login_success']}

Include potential reasons like unusual location, time, failed attempts, or device changes.
"""

    # Ollama local inference
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()
    explanation = result.get("response", "").strip()
    return explanation

if __name__ == "__main__":
    # Example usage for testing
    test_record = {
        "timestamp": "2025-07-21 03:00:00",
        "user_id": "user_17",
        "ip_address": "103.21.244.0",
        "geo_location": "China",
        "device": "Android",
        "attempt_count": 12,
        "login_success": 0
    }

    explanation = explain_anomaly(test_record)
    print("[✔] Explanation generated:\n")
    print(explanation)
