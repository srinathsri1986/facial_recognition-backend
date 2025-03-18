import os

# Get the absolute path of the current script (backend directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ensures the script runs in the correct directory
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")  # Constructs the correct uploads directory

# Construct absolute paths
photo_path = os.path.join(UPLOADS_DIR, "photo", "srinathcomms@gmail.com_photo.jpg")
resume_path = os.path.join(UPLOADS_DIR, "resume", "srinathcomms@gmail.com_resume.pdf")
id_proof_path = os.path.join(UPLOADS_DIR, "id_proof", "srinathcomms@gmail.com_id.jpg")

print(f"📷 Photo Exists: {os.path.exists(photo_path)} → Path: {photo_path}")
print(f"📄 Resume Exists: {os.path.exists(resume_path)} → Path: {resume_path}")
print(f"🆔 ID Proof Exists: {os.path.exists(id_proof_path)} → Path: {id_proof_path}")
