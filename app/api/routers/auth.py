from fastapi import APIRouter
from app.domain.schemas import LoginRequest
import uuid

router = APIRouter()

@router.post("/login")
async def login_endpoint(request: LoginRequest):
    """
    Simulated login following hack.chat style.
    Generates a deterministic UUID from username and secret key.
    """
    combined = f"{request.username}:{request.secret_key}"
    # Using NAMESPACE_OID for deterministic UUID generation from string
    user_id = str(uuid.uuid5(uuid.NAMESPACE_OID, combined))
    
    return {
        "status": "success",
        "username": request.username,
        "user_id": user_id,
        "session_token": user_id  # Using user_id as token for simplicity as requested
    }
