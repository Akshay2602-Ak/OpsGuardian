import os
import requests

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
EMAIL = os.getenv("EMAIL")

def send_email_alert(message):
    try:
        if not BREVO_API_KEY or not EMAIL:
            print("Email API credentials missing")
            return

        url = "https://api.brevo.com/v3/smtp/email"

        payload = {
            "sender": {
                "name": "OpsGuardian",
                "email": EMAIL
            },
            "to": [
                {
                    "email": EMAIL,
                    "name": "OpsGuardian User"
                }
            ],
            "subject": "OpsGuardian Alert",
            "htmlContent": f"""
                <h2>OpsGuardian Alert</h2>
                <p>{message}</p>
            """
        }

        headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        print("Email API status:", response.status_code)
        print("Email API response:", response.text)

    except Exception as e:
        print("Email failed:", e)