import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")  # Default Gmail SMTP
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))  # ✅ Add this with a default port
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
