from fastapi import APIRouter
from sqlalchemy.future import select
from sqlalchemy import update
from app.domain.schemas import LoginRequest
from app.adapters.database import AsyncSessionLocal, UserModel
from datetime import datetime, timedelta
import hashlib
import base64
import uuid

router = APIRouter()

@router.post("/heartbeat-off")
async def heartbeat_off(request: dict):
    """
    Explicitly marks the user as inactive.
    """
    user_id = request.get("user_id")
    if not user_id:
        return {"status": "error"}
        
    async with AsyncSessionLocal() as session:
        # Move last_active back by 20 minutes to force offline status
        past_time = datetime.utcnow() - timedelta(minutes=20)
        await session.execute(
            update(UserModel)
            .where(UserModel.user_id == user_id)
            .values(last_active=past_time)
        )
        await session.commit()
    return {"status": "success"}

# Global Salt for identity layer (like hack.chat)
TRIPCODE_SALT = "AEGen_VIBE_SALT_2026"

async def upsert_user_activity(user_id: str, nickname: str, tripcode: str):
    """
    Ensures the user exists in the identity table and updates their activity.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserModel).where(UserModel.user_id == user_id))
        user = result.scalars().first()
        if not user:
            user = UserModel(user_id=user_id, nickname=nickname, tripcode=tripcode, last_active=datetime.utcnow())
            session.add(user)
        else:
            user.nickname = nickname
            user.tripcode = tripcode
            user.last_active = datetime.utcnow()
        await session.commit()

def generate_tripcode(username: str, secret_key: str) -> str:
    """
    Generates a deterministic alphanumeric tripcode of the identity.
    SHA256(username + secret_key + SALT) -> Cleaned Alphanumeric String -> First 10 chars.
    """
    combined = f"{username}:{secret_key}:{TRIPCODE_SALT}"
    hashed = hashlib.sha256(combined.encode()).digest()
    
    # We use Base64 then strip non-alphanumeric chars to ensure a unique, 
    # hybrid string with upper/lower and numbers
    encoded = base64.b64encode(hashed).decode('utf-8')
    cleaned = "".join(char for char in encoded if char.isalnum())
    
    return cleaned[:7]

@router.post("/login")
async def login_endpoint(request: LoginRequest):
    """
    TripCode Identity Provider.
    Generates a unique tripcode and a user_id from the session details.
    """
    tripcode = generate_tripcode(request.username, request.secret_key)
    
    # Deterministic user_id for history tracking
    combined_id = f"{request.username}:{request.secret_key}"
    user_id = str(uuid.uuid5(uuid.NAMESPACE_OID, combined_id))
    
    # Persist the identity for the leaderboard/status tracking
    await upsert_user_activity(user_id, request.username, tripcode)

    return {
        "status": "success",
        "username": request.username,
        "tripcode": tripcode,
        "user_id": user_id,
        "session_token": user_id
    }
