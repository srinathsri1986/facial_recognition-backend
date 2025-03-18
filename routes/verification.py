from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from database import get_db
from models import Candidate, Match
from services.face_recognition import compare_faces

router = APIRouter()

# ✅ Perform Face Matching API
@router.post("/match/")
async def perform_face_matching(
    candidate_id: int = Form(...),
    photo_path: str = Form(...),
    video_path: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Perform face matching between candidate's photo and HR uploaded video and store result in DB.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    result = compare_faces(photo_path, video_path, db, candidate_id)  # ✅ Pass `db` and `candidate_id`

    return {"success": True, "result": result}

# ✅ Fetch Candidate's Match History
@router.get("/match/{candidate_id}")
async def get_match_history(candidate_id: int, db: Session = Depends(get_db)):
    """
    Retrieve past face matching results for a candidate.
    """
    matches = db.query(Match).filter(Match.candidate_id == candidate_id).all()

    return {"success": True, "matches": matches}
