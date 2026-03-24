from fastapi import APIRouter
from sqlalchemy.future import select
from sqlalchemy import func
from app.adapters.database import AsyncSessionLocal, UserModel, GenerateDocsHistoryModel, ExplainHistoryModel
from datetime import datetime, timedelta

router = APIRouter()

@router.get("")
async def get_leaderboard_and_activity():
    """
    Combined endpoint for Leaderboard and Active tracking.
    """
    async with AsyncSessionLocal() as session:
        # Get all registered identities
        stmt = select(UserModel).order_by(UserModel.last_active.desc())
        db_result = await session.execute(stmt)
        users = db_result.scalars().all()
        
        results = []
        for user in users:
            # Aggregate totals across logic adapters
            docs_count_stmt = select(func.count()).where(GenerateDocsHistoryModel.user_id == user.user_id)
            explain_count_stmt = select(func.count()).where(ExplainHistoryModel.user_id == user.user_id)
            
            docs_count = (await session.execute(docs_count_stmt)).scalar()
            explain_count = (await session.execute(explain_count_stmt)).scalar()
            
            # Identity Logic: Online if active in the last 15 minutes
            # Using utcnow() as func.now() in SQLite is usually UTC
            is_online = (datetime.utcnow() - user.last_active) < timedelta(minutes=15)
            
            results.append({
                "tripcode": user.tripcode,
                "nickname": user.nickname,
                "docs_count": docs_count or 0,
                "explain_count": explain_count or 0,
                "is_online": is_online,
                "last_active": user.last_active.isoformat()
            })
            
        # Discord-style sort: Online (True) first, then by last_active DESC
        results.sort(key=lambda x: (x["is_online"], x["last_active"]), reverse=True)

        return results
