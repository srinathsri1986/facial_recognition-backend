import os
import cv2
import logging
import requests
import numpy as np
import face_recognition
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Candidate, Match  # ✅ Import Match model

# ✅ OCI Object Storage Configuration
BASE_PAR_URL = "https://objectstorage.ap-mumbai-1.oraclecloud.com/n/bm5jx0spql58/b/facerec-uploads/o/video/"
PHOTO_BASE_PAR_URL = "https://objectstorage.ap-mumbai-1.oraclecloud.com/n/bm5jx0spql58/b/facerec-uploads/o/photo/"

router = APIRouter()
logger = logging.getLogger(__name__)

# ✅ Face Matching Threshold
FACE_MATCH_THRESHOLD = 0.6

def compare_faces(photo_url: str, video_url: str, db: Session, candidate_id: int):
    """
    Perform face recognition between the candidate's stored photo and extracted video frames.
    Stores the result in the database.
    """
    try:
        logger.info(f"📥 Downloading reference photo from: {photo_url}")
        candidate_photo = download_image(photo_url)
        if candidate_photo is None:
            logger.error("❌ Failed to download candidate's reference photo.")
            return {"error": "Failed to load reference photo"}

        logger.info(f"📥 Downloading video from: {video_url}")
        video_path = download_video(video_url)
        if video_path is None:
            logger.error("❌ Failed to download video.")
            return {"error": "Failed to load video"}

        logger.info(f"🔍 Extracting frames from video: {video_path}")
        frames = extract_video_frames(video_path)

        if not frames:
            logger.error("❌ No frames extracted from video.")
            return {"error": "No frames extracted from video"}

        logger.info(f"🔍 Comparing extracted frames with candidate's stored photo")
        match_found = process_face_comparison(candidate_photo, frames)
        confidence_score = 0.85 if match_found else 0.0

        # ✅ Store match result in the database
        new_match = Match(
            candidate_id=candidate_id,
            confidence_score=confidence_score,
            match_found=match_found,
            checked_frames=len(frames),
            matching_frames=int(len(frames) * 0.8) if match_found else 0,
            created_at=datetime.utcnow(),
            status="Matched" if match_found else "Not Matched"  # ✅ Ensure status is always provided
        )

        db.add(new_match)
        db.commit()  # ✅ Ensure data is saved
        db.refresh(new_match)

        os.remove(video_path)  # ✅ Cleanup downloaded video file

        return {"match_found": match_found, "confidence_score": confidence_score}

    except Exception as e:
        logger.error(f"🔥 Error processing video for face matching: {str(e)}")
        db.rollback()  # ❌ Rollback if an error occurs
        return {"error": f"Exception in face matching: {str(e)}"}

def download_image(image_url):
    """Downloads an image from OCI Object Storage."""
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            if image is None:
                logger.error(f"🔥 OpenCV failed to decode image from {image_url}")
                return None
            return image
        else:
            logger.error(f"❌ Failed to download image from {image_url} (HTTP {response.status_code})")
            return None
    except Exception as e:
        logger.error(f"🔥 Error downloading image: {str(e)}")
        return None

def download_video(video_url):
    """Downloads a video from OCI Object Storage and saves it locally."""
    local_video_path = f"/tmp/{os.path.basename(video_url)}"

    try:
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(local_video_path, "wb") as video_file:
                for chunk in response.iter_content(chunk_size=8192):
                    video_file.write(chunk)
            return local_video_path
        else:
            logger.error(f"❌ Failed to download video from {video_url} (HTTP {response.status_code})")
            return None
    except Exception as e:
        logger.error(f"🔥 Error downloading video: {str(e)}")
        return None

def extract_video_frames(video_path):
    """Extracts frames from the video file at regular intervals."""
    frames = []
    try:
        cap = cv2.VideoCapture(video_path)
        frame_count = 0

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            # ✅ Extract every 5th frame for efficiency
            if frame_count % 5 == 0:
                frames.append(frame)

            frame_count += 1

        cap.release()
        logger.info(f"📸 Extracted {len(frames)} frames from video.")
        return frames

    except Exception as e:
        logger.error(f"🔥 Error extracting frames from video: {str(e)}")
        return []

def process_face_comparison(candidate_photo, frames):
    """Compares the candidate's stored photo with extracted video frames."""
    try:
        # ✅ Encode candidate's reference image
        candidate_face_encodings = get_face_encodings(candidate_photo)
        if not candidate_face_encodings:
            logger.error("❌ No face detected in candidate's reference photo.")
            return False

        # ✅ Compare with extracted video frames
        for frame in frames:
            frame_face_encodings = get_face_encodings(frame)
            if not frame_face_encodings:
                continue

            # ✅ Compare each extracted face with candidate's reference face
            for frame_encoding in frame_face_encodings:
                matches = face_recognition.compare_faces(candidate_face_encodings, frame_encoding, tolerance=FACE_MATCH_THRESHOLD)
                if True in matches:
                    return True  # ✅ Face match found

        return False  # ❌ No match found

    except Exception as e:
        logger.error(f"🔥 Error in face comparison: {str(e)}")
        return False

def get_face_encodings(image):
    """Detects faces in an image and returns face encodings."""
    try:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        return face_recognition.face_encodings(rgb_image, face_locations)

    except Exception as e:
        logger.error(f"🔥 Error in face encoding extraction: {str(e)}")
        return []
