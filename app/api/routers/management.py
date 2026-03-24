from fastapi import APIRouter
from sqlalchemy import text
from app.adapters.database import AsyncSessionLocal, Base

router = APIRouter()

@router.post("/nuke-data")
async def nuke_data():
    """
    Clears all data from all known tables in the database.
    Does NOT drop the tables themselves.
    This effectively resets the application state (leaderboard, history, sessions).
    """
    async with AsyncSessionLocal() as session:
        # We iterate through all tables to delete their contents
        # Using text() for raw SQL performance on bulk clear
        for table in Base.metadata.sorted_tables:
            await session.execute(text(f"DELETE FROM {table.name}"))
        
        # Reset sqlite sequences if any tables use AUTOINCREMENT
        try:
            await session.execute(text("DELETE FROM sqlite_sequence"))
        except Exception:
            pass
        
        await session.commit()
        
    return {
        "status": "success", 
        "message": "Project reset successful. All database records have been cleared."
    }
