from fastapi import APIRouter, Depends, HTTPException, Query, Form, Path
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from database import get_db
from models import Candidate, Match
from services.face_recognition import compare_faces
from datetime import datetime

router = APIRouter()

# ✅ GET /match/all — All Matches (with filters + candidate details + pagination metadata)
@router.get("/match/all")
async def get_all_match_history(
    candidate_id: int = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    min_confidence: float = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    filters = []

    if candidate_id:
        filters.append(Match.candidate_id == candidate_id)

    if start_date:
        try:
            filters.append(Match.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD.")

    if end_date:
        try:
            filters.append(Match.created_at <= datetime.strptime(end_date, "%Y-%m-%d"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD.")

    if min_confidence is not None:
        filters.append(Match.confidence_score >= min_confidence)

    query = db.query(Match).options(joinedload(Match.candidate))
    if filters:
        query = query.filter(and_(*filters))

    total_count = query.count()
    matches = query.order_by(Match.created_at.desc()).offset(offset).limit(limit).all()

    results = []
    for match in matches:
        c = match.candidate
        results.append({
            "id": match.id,
            "candidate_id": match.candidate_id,
            "confidence_score": match.confidence_score,
            "match_found": match.match_found,
            "matching_frames": match.matching_frames,
            "checked_frames": match.checked_frames,
            "status": match.status,
            "created_at": match.created_at,
            "candidate": {
                "id": c.id,
                "first_name": c.first_name,
                "last_name": c.last_name,
                "email": c.email,
                "phone": c.phone,
                "photo": c.photo,
                "verified": c.verified,
            }
        })

    return {
        "success": True,
        "count": len(results),
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "matches": results
    }


# ✅ GET /match/{candidate_id} — Match History for One Candidate
@router.get("/match/{candidate_id}")
async def get_match_history_for_candidate(
    candidate_id: int = Path(...),
    db: Session = Depends(get_db)
):
    matches = (
        db.query(Match)
        .options(joinedload(Match.candidate))
        .filter(Match.candidate_id == candidate_id)
        .order_by(Match.created_at.desc())
        .all()
    )

    if not matches:
        raise HTTPException(status_code=404, detail="No match records found for the candidate")

    results = []
    for match in matches:
        c = match.candidate
        results.append({
            "id": match.id,
            "candidate_id": match.candidate_id,
            "confidence_score": match.confidence_score,
            "match_found": match.match_found,
            "matching_frames": match.matching_frames,
            "checked_frames": match.checked_frames,
            "status": match.status,
            "created_at": match.created_at,
            "candidate": {
                "id": c.id,
                "first_name": c.first_name,
                "last_name": c.last_name,
                "email": c.email,
                "phone": c.phone,
                "photo": c.photo,
                "verified": c.verified,
            }
        })

    return {
        "success": True,
        "count": len(results),
        "matches": results
    }


# ✅ POST /match/ — Perform face match and update verified status
@router.post("/match/")
async def perform_face_matching(
    candidate_id: int = Form(...),
    photo_path: str = Form(...),
    video_path: str = Form(...),
    db: Session = Depends(get_db),
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    result = compare_faces(photo_path, video_path, db, candidate_id)
    print("Face Match Result:", result)

    if result.get("match_found") and result.get("confidence_score", 0.0) >= 0.8:
        candidate.verified = True
        db.commit()

    return {"success": True, "result": result}
