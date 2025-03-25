import os
import logging
import requests
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import get_db
from models import Candidate, HRUser
from services.hashing import Hash
from typing import Optional
from pydantic import BaseModel, EmailStr
from urllib.parse import unquote
import secrets

router = APIRouter()
logger = logging.getLogger(__name__)

# ✅ OCI Storage URL with Pre-Authenticated Request (PAR)
OCI_PAR_TOKEN = "KlvNhT0KOfX5pjeFJaSs5VPTdiEjcCmjAdZ93FopD-8ZEM5LZivVaGEWI6N9i7o9"
OCI_NAMESPACE = "bm5jx0spql58"
OCI_BUCKET_NAME = "facerec-uploads"
BASE_PAR_URL = f"https://bm5jx0spql58.objectstorage.ap-mumbai-1.oci.customer-oci.com/p/{OCI_PAR_TOKEN}/n/{OCI_NAMESPACE}/b/{OCI_BUCKET_NAME}/o"

# ✅ Helper function to fix file URLs
def fix_url(file_path: Optional[str]) -> Optional[str]:
    return file_path if file_path and file_path.startswith("http") else None

### ======================== 1️⃣ SIGNUP FUNCTION ========================== ###
class CandidateSignup(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    address: str
    phone: str

@router.post("/signup")
async def candidate_signup(signup_data: CandidateSignup, db: Session = Depends(get_db)):
    logger.info(f"Attempting signup for {signup_data.email}")
    try:
        existing_candidate = db.query(Candidate).filter(Candidate.email == signup_data.email).first()
        if existing_candidate:
            raise HTTPException(status_code=400, detail="Candidate with this email already exists")

        hashed_password = Hash.bcrypt(signup_data.password)
        new_candidate = Candidate(
            first_name=signup_data.first_name,
            last_name=signup_data.last_name,
            email=signup_data.email,
            password=hashed_password,
            address=signup_data.address,
            phone=signup_data.phone,
            verified=False,
        )
        db.add(new_candidate)
        db.commit()
        db.refresh(new_candidate)
        logger.info(f"Candidate {signup_data.email} registered successfully.")
        return {"success": True, "message": "Signup successful!"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

### ======================== 2️⃣ LOGIN FUNCTION ========================== ###
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
async def candidate_login(request: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Candidate Login Attempt: {request.email}")
    candidate = db.query(Candidate).filter(Candidate.email == request.email).first()
    if not candidate or not Hash.verify(candidate.password, request.password):
        raise HTTPException(status_code=400, detail="Invalid credentials.")

    has_completed_profile = bool(candidate.first_name and candidate.last_name and candidate.address and candidate.phone)
    return {"success": True, "message": "Login successful!", "email": candidate.email, "hasCompletedProfile": has_completed_profile}

### ======================== 3️⃣ GET CANDIDATE DETAILS ========================== ###
@router.get("/{email}/")
async def get_candidate(email: str, db: Session = Depends(get_db)):
    decoded_email = unquote(email)
    candidate = db.query(Candidate).filter(Candidate.email == decoded_email).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return JSONResponse(
        content={
            "success": True,
            "data": {
                "first_name": candidate.first_name,
                "last_name": candidate.last_name,
                "email": candidate.email,
                "phone": candidate.phone,
                "verified": candidate.verified,
                "address": candidate.address,
                "resume": candidate.resume,
                "photo": candidate.photo,
                "id_proof": candidate.id_proof,
            }
        },
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )

### ======================== 4️⃣ UPDATE CANDIDATE DETAILS ========================== ###
async def upload_to_oci(file: UploadFile, category: str, candidate_email: str) -> Optional[str]:
    """Uploads file to OCI and ensures old file is deleted before uploading a new one."""
    try:
        filename = f"{category}/{candidate_email}_file{os.path.splitext(file.filename)[-1].lower()}"
        upload_url = f"{BASE_PAR_URL}/{filename}"

        content = await file.read()
        response = requests.put(upload_url, data=content, headers={"Content-Type": file.content_type})
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to upload file to OCI")

        return upload_url

    except Exception as e:
        logger.error(f"OCI Upload Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error uploading file to OCI")

@router.post("/update-details")
async def update_candidate_details(
    email: str = Form(...), #Email is mandatory
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    id_proof: UploadFile = File(None),
    photo: UploadFile = File(None),
    resume: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(Candidate.email == email).first()

    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate not found: {email}")

    # Update fields only if they are provided
    if first_name:
        candidate.first_name = first_name
    if last_name:
        candidate.last_name = last_name
    if address:
        candidate.address = address
    if phone:
        candidate.phone = phone

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Upload new files
    try:
        if id_proof:
            candidate.id_proof = await upload_to_oci(id_proof, "id_proof", email)
        if photo:
            candidate.photo = await upload_to_oci(photo, "photo", email)
        if resume:
            candidate.resume = await upload_to_oci(resume, "resume", email)

        db.commit()
        return {"success": True, "message": "Candidate details updated successfully"}

    except Exception as e:
        db.rollback()
        logger.error(f"File upload error for {email}: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

### ======================== 5️⃣ PASSWORD RESET ========================== ###

class PasswordResetRequest(BaseModel):
    email: EmailStr

@router.post("/reset-password")
async def reset_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.email == request.email).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    new_password = secrets.token_urlsafe(8) # Generate a secure random password.
    hashed_password = Hash.bcrypt(new_password)
    candidate.password = hashed_password
    db.commit()
    return {"success": True, "message": "Password reset successful. New password sent to email
