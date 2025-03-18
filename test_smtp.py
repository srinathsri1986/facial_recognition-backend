import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# ✅ Load .env variables
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# ✅ Email Details
TO_EMAIL = "srinath.cx@gmail.com"  # Change this to a valid email
SUBJECT = "Test Email from Python"
BODY = "Hello! This is a test email sent from my Python script."

# ✅ Create Email
msg = EmailMessage()
msg["Subject"] = SUBJECT
msg["From"] = SMTP_EMAIL
msg["To"] = TO_EMAIL
msg.set_content(BODY)

try:
    print("🔄 Sending test email...")
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
    print(f"✅ Test email sent to {TO_EMAIL}")
except Exception as e:
    print(f"❌ Email sending failed: {e}")
