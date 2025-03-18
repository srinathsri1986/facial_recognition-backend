import requests
import base64
import certifi
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Zoom API Credentials
ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")

# ✅ Function to Get Zoom OAuth Token
def get_zoom_access_token():
    if not ZOOM_CLIENT_ID or not ZOOM_CLIENT_SECRET or not ZOOM_ACCOUNT_ID:
        raise ValueError("Zoom credentials are missing. Check your .env file.")

    url = "https://zoom.us/oauth/token"
    auth_header = base64.b64encode(f"{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "account_credentials", "account_id": ZOOM_ACCOUNT_ID}

    response = requests.post(url, headers=headers, data=data, verify=certifi.where())

    if response.status_code == 200:
        return response.json().get("access_token")
    
    raise ValueError(f"Zoom Auth Error: {response.json()}")

# ✅ Function to Schedule a Zoom Meeting
def create_zoom_meeting(candidate_email: str, interviewer_email: str, start_time: str):
    """Creates a Zoom meeting with given candidate and interviewer details."""
    
    try:
        access_token = get_zoom_access_token()
    except ValueError as e:
        return {"error": str(e)}

    url = "https://api.zoom.us/v2/users/me/meetings"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "topic": f"HR Interview with {candidate_email}",
        "type": 2,
        "start_time": start_time,
        "duration": 30,
        "timezone": "UTC",
        "agenda": "Candidate face verification interview",
        "settings": {
            "host_video": True,
            "participant_video": True,
            "waiting_room": True,
            "mute_upon_entry": True,
            "registrants_email_notification": True
        }
    }

    response = requests.post(url, headers=headers, json=payload, verify=certifi.where())

    if response.status_code == 201:
        return response.json()
    
    return {"error": f"Zoom Meeting Error: {response.json()}"}
