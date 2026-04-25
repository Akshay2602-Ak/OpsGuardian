import os
import requests

API_KEY = os.getenv("RESEND_API_KEY")
EMAIL = os.getenv("EMAIL")

def send_email_alert(message):
    try:
        url = "https://api.resend.com/emails"

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "from": "OpsGuardian <onboarding@resend.dev>",
            "to": [EMAIL],
            "subject": "🚨 OpsGuardian Alert",
            "html": f"<h3>{message}</h3>"
        }

        res = requests.post(url, json=payload, headers=headers)

        print("Email status:", res.status_code)
        print("Response:", res.text)

    except Exception as e:
        print("Email failed:", e)