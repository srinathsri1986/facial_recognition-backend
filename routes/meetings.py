import logging
from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from sqlalchemy.orm import Session
from database import get_db
from models import Meeting
from services.zoom_service import create_zoom_meeting
from datetime import datetime
from services.email_service import EmailService

router = APIRouter()
logger = logging.getLogger(__name__)

# ✅ Function to Retrieve `email_service` from `app.state`
def get_email_service(request: Request):
    return request.app.state.email_service  # ✅ Access `app.state.email_service` dynamically

# ✅ POST: Schedule a Zoom Meeting & Store in Database
@router.post("/schedule/")
async def create_meeting(
    candidate_id: int = Form(...),
    candidate_email: str = Form(...), 
    interviewer_email: str = Form(...), 
    start_time: str = Form(...),
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service)  # ✅ Use request.app.state
):
    """Schedule a new Zoom meeting, save details in the database, and send invites via email."""
    logger.info(f"📅 Scheduling meeting for {candidate_email} at {start_time}")

    # ✅ Schedule the Zoom meeting
    meeting_data = create_zoom_meeting(candidate_email, interviewer_email, start_time)

    # ✅ Ensure the meeting was successfully created
    if "id" not in meeting_data:
        logger.error("❌ Failed to create Zoom meeting.")
        raise HTTPException(status_code=500, detail="Failed to schedule meeting")

    # ✅ Convert `start_time` to proper format
    try:
        formatted_start_time = datetime.fromisoformat(start_time)
    except ValueError:
        logger.error("❌ Invalid start_time format")
        raise HTTPException(status_code=400, detail="Invalid start_time format")

    # ✅ Save meeting in database
    new_meeting = Meeting(
        id=int(meeting_data["id"]) % 2147483647,  # ✅ Ensure it fits in INTEGER range
        candidate_id=candidate_id,
        start_time=formatted_start_time,
        join_url=meeting_data["join_url"],
        password=meeting_data["password"]
    )

    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)
    logger.info(f"✅ Meeting {new_meeting.id} saved successfully.")

    # ✅ Prepare email content
    email_subject = f"Zoom Interview Scheduled: {meeting_data['topic']}"
    email_body = f"""
    Dear Participant,

    Your Zoom interview has been scheduled.

    📅 Date & Time: {start_time}
    🔗 Join URL: {meeting_data["join_url"]}
    🔑 Meeting Password: {meeting_data["password"]}

    Please be available at the scheduled time.

    Best regards,  
    ACL Digital Recruitment Team
    """

    # ✅ Send email to candidate & interviewer
    try:
        email_service.send_email(candidate_email, email_subject, email_body)
        email_service.send_email(interviewer_email, email_subject, email_body)
        logger.info(f"📧 Email invite sent to {candidate_email} and {interviewer_email}")
    except Exception as e:
        logger.error(f"❌ Failed to send meeting invite email: {e}")
        raise HTTPException(status_code=500, detail="Email sending failed")

    # ✅ Return success response
    return {
        "success": True, 
        "meeting_id": new_meeting.id, 
        "meeting_link": new_meeting.join_url
    }
