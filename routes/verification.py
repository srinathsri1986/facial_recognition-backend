from fastapi import APIRouter, Depends, HTTPException, Query, Form
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from database import get_db
from models import Candidate, Match
from services.face_recognition import compare_faces
from datetime import datetime

router = APIRouter()

# ✅ Fetch Match History for All Candidates with Optional Filters + Join with Candidate
@router.get("/match/all")
async def get_all_match_history(
    candidate_id: int = Query(None, description="Filter by specific candidate ID"),
    start_date: str = Query(None, description="Start date in YYYY-MM-DD"),
    end_date: str = Query(None, description="End date in YYYY-MM-DD"),
    min_confidence: float = Query(None, description="Minimum confidence score (0.0 to 1.0)"),
    limit: int = Query(100, description="Max results to return"),
    offset: int = Query(0, description="Results offset for pagination"),
    db: Session = Depends(get_db),
):
    """
    Retrieve all face matching results across candidates with optional filters.
    Includes candidate details for each match result.
    """
    filters = []

    if candidate_id:
        filters.append(Match.candidate_id == candidate_id)

    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            filters.append(Match.created_at >= start_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD.")

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            filters.append(Match.created_at <= end_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD.")

    if min_confidence is not None:
        filters.append(Match.confidence_score >= min_confidence)

    query = db.query(Match).options(joinedload(Match.candidate))
    if filters:
        query = query.filter(and_(*filters))

    matches = query.order_by(Match.created_at.desc()).offset(offset).limit(limit).all()

    result = []
    for match in matches:
        result.append({
            "id": match.id,
            "candidate_id": match.candidate_id,
            "confidence_score": match.confidence_score,
            "match_found": match.match_found,
            "matching_frames": match.matching_frames,
            "checked_frames": match.checked_frames,
            "status": match.status,
            "created_at": match.created_at,
            "candidate": {
                "id": match.candidate.id,
                "first_name": match.candidate.first_name,
                "last_name": match.candidate.last_name,
                "email": match.candidate.email,
                "phone": match.candidate.phone,
                "photo": match.candidate.photo,
                "verified": match.candidate.verified,
            }
        })

    return {
        "success": True,
        "count": len(result),
        "matches": result
    }
