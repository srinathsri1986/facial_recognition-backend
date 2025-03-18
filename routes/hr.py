import logging
from fastapi import APIRouter, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import HRUser, Candidate, Meeting, Match
from services.hashing import Hash
from services.zoom_service import create_zoom_meeting
from utils.file_utils import fix_oci_url  # ✅ Correct absolute import
from pydantic import BaseModel
from datetime import datetime
from dateutil import parser

router = APIRouter()
logger = logging.getLogger(__name__)

# ✅ HR Login Model
class HRLoginRequest(BaseModel):
    email: str
    password: str

# ✅ HR Login API
@router.post("/login")
async def hr_login(request: HRLoginRequest, db: Session = Depends(get_db)):
    hr_user = db.query(HRUser).filter(HRUser.email == request.email).first()
    if not hr_user or not Hash.verify(hr_user.password, request.password):
        raise HTTPException(status_code=400, detail="Invalid credentials.")
    return {"success": True, "message": "HR Login successful!", "email": hr_user.email}

# ✅ Get All Candidates (Uses `fix_oci_url()`)
@router.get("/candidates")
async def get_all_candidates(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": c.id,
                "first_name": c.first_name,
                "last_name": c.last_name,
                "email": c.email,
                "photo": fix_oci_url(c.email, "photo", c.photo.split(".")[-1]) if c.photo else None,
                "resume": fix_oci_url(c.email, "resume", c.resume.split(".")[-1]) if c.resume else None,
                "id_proof": fix_oci_url(c.email, "id_proof", c.id_proof.split(".")[-1]) if c.id_proof else None,
                "verified": c.verified,
            }
            for c in candidates
        ]
    }

# ✅ Get Candidate by ID (Uses `fix_oci_url()`)
@router.get("/candidate/{candidate_id}")
async def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return {
        "success": True,
        "data": {
            "id": candidate.id,
            "first_name": candidate.first_name,
            "last_name": candidate.last_name,
            "email": candidate.email,
            "photo": fix_oci_url(candidate.email, "photo", candidate.photo.split(".")[-1]) if candidate.photo else None,
            "resume": fix_oci_url(candidate.email, "resume", candidate.resume.split(".")[-1]) if candidate.resume else None,
            "id_proof": fix_oci_url(candidate.email, "id_proof", candidate.id_proof.split(".")[-1]) if candidate.id_proof else None,
            "verified": candidate.verified,
        }
    }

# ✅ Schedule a Zoom Meeting
@router.post("/meetings/schedule/")
async def schedule_meeting(
    candidate_id: int = Form(...),
    candidate_email: str = Form(...),
    interviewer_email: str = Form(...),
    start_time: str = Form(...),
    db: Session = Depends(get_db),
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    try:
        parsed_start_time = parser.isoparse(start_time.replace("Z", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date-time format. Use ISO 8601 format.")

    meeting_data = create_zoom_meeting(candidate_email, interviewer_email, parsed_start_time.isoformat())
    if "error" in meeting_data:
        raise HTTPException(status_code=400, detail=meeting_data["error"])

    new_meeting = Meeting(
        candidate_id=candidate.id,
        start_time=parsed_start_time,
        scheduled_at=parsed_start_time.isoformat(),
        join_url=meeting_data["join_url"],
        password=meeting_data.get("password"),
    )
    
    try:
        db.add(new_meeting)
        db.commit()
        db.refresh(new_meeting)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while scheduling meeting")

    return {
        "success": True,
        "meeting_id": new_meeting.id,
        "meeting_link": meeting_data["join_url"],
        "start_time": parsed_start_time.isoformat(),
    }

# ✅ Get All Meetings
@router.get("/meetings")
async def get_all_meetings(db: Session = Depends(get_db)):
    """Fetch all meetings."""
    meetings = db.query(Meeting).all()
    return {
        "success": True,
        "data": [
            {
                "id": m.id,
                "candidate_id": m.candidate_id,
                "scheduled_at": m.scheduled_at,
                "start_time": m.start_time,
                "join_url": m.join_url,
                "password": m.password,
            }
            for m in meetings
        ]
    }

# ✅ Delete a Meeting
@router.delete("/meetings/{meeting_id}")
async def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """Deletes a scheduled meeting."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    db.delete(meeting)
    db.commit()
    return {"success": True, "message": "Meeting deleted successfully"}

# ✅ Get Candidates' Match Status (Uses `fix_oci_url()`)
@router.get("/candidates/match-status")
async def get_candidates_match_status(db: Session = Depends(get_db)):
    """
    Fetch candidates along with their verification status and face match details.
    """
    results = db.query(
        Candidate.id, 
        Candidate.first_name, 
        Candidate.last_name, 
        Candidate.email, 
        Candidate.verified,
        Match.match_found, 
        Match.confidence_score, 
        Match.status, 
        Match.checked_frames, 
        Match.matching_frames, 
        Match.created_at,
        Candidate.photo,  
        Candidate.resume,  
        Candidate.id_proof  
    ).outerjoin(Match, Candidate.id == Match.candidate_id).order_by(Candidate.id).all()

    return {
        "success": True,
        "data": [
            {
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "verified": row[4],
                "match_found": row[5],
                "confidence_score": round(float(row[6]), 2) if row[6] is not None else 0.00, 
                "status": row[7],
                "checked_frames": row[8],
                "matching_frames": row[9],
                "created_at": row[10],
                "photo": fix_oci_url(row[3], "photo", "jpg") if row[11] else None,
                "resume": fix_oci_url(row[3], "resume", row[12].split(".")[-1]) if row[12] else None,
                "id_proof": fix_oci_url(row[3], "id_proof", "jpg") if row[13] else None
            }
            for row in results
        ]
    }
