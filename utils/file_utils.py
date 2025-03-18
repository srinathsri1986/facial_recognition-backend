import os
import logging
import requests
from fastapi import UploadFile, HTTPException

# ✅ Base OCI Object Storage URL
OCI_PAR_TOKEN = "KlvNhT0KOfX5pjeFJaSs5VPTdiEjcCmjAdZ93FopD-8ZEM5LZivVaGEWI6N9i7o9"
OCI_NAMESPACE = "bm5jx0spql58"
OCI_BUCKET_NAME = "facerec-uploads"
BASE_PAR_URL = f"https://bm5jx0spql58.objectstorage.ap-mumbai-1.oci.customer-oci.com/p/{OCI_PAR_TOKEN}/n/{OCI_NAMESPACE}/b/{OCI_BUCKET_NAME}/o/"

def fix_oci_url(email: str, category: str, actual_ext: str) -> str:
    """
    Generates the correct OCI Object Storage URL dynamically using the actual stored file extension.

    :param email: Candidate's email (used to generate filename)
    :param category: One of ["photo", "resume", "id_proof", "video"]
    :param actual_ext: The actual extension stored in OCI
    :return: Fully formatted OCI Object Storage URL
    """

    category_mapping = {
        "photo": "photo",
        "resume": "resume",
        "id_proof": "id_proof",
        "video": "video"
    }

    if category not in category_mapping:
        return None  # If category is invalid, return None

    folder = category_mapping[category]

    # ✅ Ensure correct file extension
    extension = actual_ext.lower().lstrip(".") if actual_ext else "jpg" if category == "photo" else "pdf"

    return f"{BASE_PAR_URL}{folder}/{email}_file.{extension}"
