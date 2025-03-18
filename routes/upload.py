import os
import logging
import requests
from fastapi import APIRouter, UploadFile, HTTPException, Form, File
from utils.file_utils import fix_oci_url  # ✅ Correct absolute import

# ✅ Define allowed file extensions & size limits
ALLOWED_EXTENSIONS = {
    "photo": {"jpg", "jpeg", "png"},
    "resume": {"pdf", "doc", "docx"},
    "id_proof": {"jpg", "jpeg", "png"},
    "video": {"mp4", "avi", "mkv", "mov", "webm"}
}

MAX_FILE_SIZE_MB = 100  # ✅ 100MB limit
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to Bytes

# ✅ Logger Setup
logger = logging.getLogger(__name__)

# ✅ Initialize API Router
router = APIRouter()

# ✅ Function to Upload File to OCI
async def save_file(file: UploadFile, email: str, category: str) -> str:
    """Uploads a file to OCI Object Storage and returns the correct public URL."""

    category_mapping = {
        "id_proof": "id_proof",
        "photo": "photo",
        "resume": "resume",
        "video": "video"
    }

    # ✅ Validate category
    if category not in category_mapping:
        raise HTTPException(status_code=400, detail=f"Invalid file category: {category}")

    mapped_category = category_mapping[category]

    # ✅ Extract File Extension
    ext = os.path.splitext(file.filename)[-1].lower().lstrip(".")
    if ext not in ALLOWED_EXTENSIONS[mapped_category]:
        raise HTTPException(status_code=400, detail=f"File type .{ext} not allowed")

    # ✅ Read file content to check size
    file_content = await file.read()
    file_size = len(file_content)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File size exceeds {MAX_FILE_SIZE_MB}MB limit")

    # ✅ Correct Filename Format
    oci_object_name = f"{mapped_category}/{email}_file.{ext}"

    # ✅ Construct Upload URL
    upload_url = fix_oci_url(email, category, ext)  # ✅ Ensure the correct OCI URL format

    # ✅ Upload to OCI Object Storage
    headers = {"Content-Type": file.content_type}
    response = requests.put(upload_url, data=file_content, headers=headers)

    if response.status_code != 200:
        logger.error(f"❌ OCI Upload Failed: {response.status_code} - {response.text}")
        raise HTTPException(status_code=500, detail="Failed to upload file to OCI Object Storage")

    logger.info(f"✅ File uploaded to OCI: {upload_url}")

    # ✅ Return the correct OCI URL
    return upload_url

# ✅ Upload API Endpoint
@router.post("/upload/{category}")
async def upload_file(category: str, email: str = Form(...), file: UploadFile = File(...)):
    """Handles file upload for candidates and HR users."""
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    oci_url = await save_file(file, email, category)

    return {"success": True, "file_url": oci_url}
