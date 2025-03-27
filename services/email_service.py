import smtplib
import logging
import traceback
from email.message import EmailMessage
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD

logger = logging.getLogger(__name__)

class EmailSendingError(Exception):
    """Custom exception for email sending failures."""
    pass

class EmailService:
    def __init__(self, smtp_server, smtp_port, smtp_username, smtp_password, sender_email):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.sender_email = sender_email

    def send_email(self, recipient_email, subject, body):
        """Send an email to the specified recipient."""
        logger.info(f"📧 Preparing to send email to {recipient_email} with subject: {subject}")

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.sender_email  # ✅ FIXED: Using correct sender_email
        msg["To"] = recipient_email
        msg.set_content(body)

        try:
            logger.info("🔄 Connecting to SMTP server...")
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                logger.info(f"✅ Connected to {self.smtp_server}. Logging in...")
                server.login(self.smtp_username, self.smtp_password)
                logger.info("✅ SMTP Login Successful. Sending Email...")
                server.send_message(msg)
                logger.info(f"✅ Email sent successfully to {recipient_email}")
        except Exception as e:
            logger.error(f"❌ Email sending failed: {e}\n{traceback.format_exc()}")
            raise EmailSendingError("Email sending failed")

# ✅ Updated function to use EmailService instead of direct SMTP login
def send_email_notification(email_service: EmailService, candidate_email, interviewer_email, meeting_data):
    subject = f"Zoom Interview Scheduled: {meeting_data['topic']}"
    
    email_body = f"""
    Dear Candidate,

    Your Zoom interview has been scheduled.

    📅 Date & Time: {meeting_data["start_time"]}
    🔗 Join URL: {meeting_data["join_url"]}
    🔑 Meeting Password: {meeting_data["password"]}

    Please be available at the scheduled time.

    Best regards,  
    ACL Digital Recruitment Team
    """

    # ✅ Use EmailService instead of direct SMTP connection
    try:
        email_service.send_email(candidate_email, subject, email_body)
        email_service.send_email(interviewer_email, subject, email_body)
        logger.info(f"📧 Email invite sent to {candidate_email} and {interviewer_email}")
    except Exception as e:
        logger.error(f"❌ Failed to send meeting invite email: {e}")
        raise EmailSendingError("Email sending failed")
