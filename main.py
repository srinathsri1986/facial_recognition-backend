import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from routes import upload, verification, candidate, hr, meetings
from database import engine, Base
from services.email_service import EmailService
from utils.logging_config import logger  # ✅ Use existing logger (No need for setup_logging())

# ✅ Load Environment Variables
load_dotenv()

logger.info("✅ FastAPI server is starting...")

# ✅ Ensure "uploads" folder exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Initialize FastAPI
app = FastAPI(
    title="Facial Recognition API",
    version="1.0.0",
    description="API for facial recognition, video verification, and Zoom meeting scheduling.",
)

# ✅ CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Create database tables on startup
@app.on_event("startup")
def startup_event():
    logger.info("📂 Creating database tables (if not exist)...")
    Base.metadata.create_all(bind=engine)

    # ✅ Check Environment Variables
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_server or not smtp_port or not smtp_email or not smtp_password:
        logger.error("❌ SMTP configuration is missing! Check .env file.")
    else:
        logger.info(f"📧 SMTP Config Loaded: {smtp_server}:{smtp_port} as {smtp_email}")

    # ✅ Initialize Email Service
    app.state.email_service = EmailService(
        smtp_server=smtp_server,
        smtp_port=int(smtp_port),
        smtp_username=smtp_email,
        smtp_password=smtp_password,
        sender_email=smtp_email,
    )
    logger.info("📧 Email service initialized.")

# ✅ Mount Static Files
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

# ✅ Include API Routers
app.include_router(hr.router, prefix="/api/hr", tags=["HR"])
app.include_router(verification.router, prefix="/api/verification", tags=["Verification"])
app.include_router(candidate.router, prefix="/api/candidate", tags=["Candidate"])
app.include_router(upload.router, prefix="/api/uploads", tags=["Uploads"])
app.include_router(meetings.router, prefix="/api/meetings", tags=["Meetings"])

# ✅ Root Endpoint (Health Check)
@app.get("/", tags=["Health"])
async def root():
    logger.info("✅ Health check endpoint was accessed.")
    return {"message": "Facial Recognition API is running!"}
