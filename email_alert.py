import smtplib

EMAIL = "bro998510@gmail.com"
PASSWORD = "btamcktuxafxjrdd"

def send_email_alert(message):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(EMAIL, PASSWORD)

        subject = "OpsGuardian Alert 🚨"
        msg = f"Subject: {subject}\n\n{message}"

        server.sendmail(EMAIL, EMAIL, msg)
        server.quit()

        print("✅ Email sent")

    except Exception as e:
        print("❌ Email failed:", e)