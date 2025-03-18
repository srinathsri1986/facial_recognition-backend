from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# ✅ Candidate Table
class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(500), nullable=False)
    resume = Column(Text, nullable=True)
    photo = Column(Text, nullable=True)
    id_proof = Column(Text, nullable=True)
    password = Column(String(255), nullable=False)
    verified = Column(Boolean, default=False)

    # ✅ Relationships
    meetings = relationship("Meeting", back_populates="candidate", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="candidate", cascade="all, delete-orphan")

# ✅ Meeting Table
class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    scheduled_at = Column(DateTime, default=datetime.utcnow)  # ✅ Fixed: Changed from `String` to `DateTime`
    join_url = Column(Text, nullable=False)  # ✅ Fixed: Increased limit for long Zoom URLs
    password = Column(String(50), nullable=True)  # ✅ Fixed: Allow `NULL` passwords in case Zoom doesn’t return

    # ✅ Relationship
    candidate = relationship("Candidate", back_populates="meetings")

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    confidence_score = Column(Float, nullable=False)
    match_found = Column(Boolean, nullable=False, default=False)
    checked_frames = Column(Integer, default=0)
    matching_frames = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), nullable=False, default="Not Matched")  # ✅ Ensure default is provided

    # ✅ Relationship
    candidate = relationship("Candidate", back_populates="matches")

# ✅ Backend User Table
class BackendUser(Base):
    __tablename__ = "backend_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

# ✅ HR User Table
class HRUser(Base):
    __tablename__ = "hr_users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Stores hashed password
    phone = Column(String(20), nullable=True)
    role = Column(String(50), default="hr")
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
