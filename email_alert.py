import smtplib
import os

EMAIL = os.getenv("bro998510@gmail.com")
PASSWORD = os.getenv("zvfwzuusxqqdqmnu")

def send_email_alert(message):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login(EMAIL, PASSWORD)

        subject = "🚨 OpsGuardian Alert"
        msg = f"Subject: {subject}\n\n{message}"

        server.sendmail(EMAIL, EMAIL, msg)

        server.quit()

        print("✅ Email sent:", message)

    except Exception as e:
        print("❌ Email error:", e)