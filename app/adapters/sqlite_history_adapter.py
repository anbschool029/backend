from app.ports.history_port import HistoryPort
from app.adapters.database import AsyncSessionLocal, GenerateDocsHistoryModel, ExplainHistoryModel, UserModel
from sqlalchemy.future import select
from sqlalchemy import delete, update
from datetime import datetime

class SQLiteHistoryAdapter(HistoryPort):
    """
    Fulfills the HistoryPort contract utilizing explicit asynchronous SQLAlchemy calls.
    Now updated to handle project and file IDs for a more organized nomad workspace.
    """
    
    async def update_user_heartbeat(self, user_id: str):
        """Internal helper to keep 'Active Board' in sync on every action."""
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(UserModel)
                .where(UserModel.user_id == user_id)
                .values(last_active=datetime.utcnow())
            )
            await session.commit()

    async def create_generate_docs_history(self, code: str, styles: str, custom_style: str, result: str, user_id: str, project_id: str = None, file_id: str = None) -> str:
        await self.update_user_heartbeat(user_id)
        async with AsyncSessionLocal() as session:
            new_record = GenerateDocsHistoryModel(
                incoming_code=code,
                styles_used=styles,
                custom_style_used=custom_style,
                ai_response=result,
                user_id=user_id,
                project_id=project_id,
                file_id=file_id
            )
            session.add(new_record)
            await session.commit()
            return new_record.id

    async def create_explain_history(self, code: str, styles: str, custom_style: str, result: str, user_id: str, project_id: str = None, file_id: str = None) -> str:
        await self.update_user_heartbeat(user_id)
        async with AsyncSessionLocal() as session:
            new_record = ExplainHistoryModel(
                incoming_code=code,
                styles_used=styles,
                custom_style_used=custom_style,
                ai_response=result,
                user_id=user_id,
                project_id=project_id,
                file_id=file_id
            )
            session.add(new_record)
            await session.commit()
            return new_record.id

    async def get_docs_history(self, history_id: str) -> dict | None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(GenerateDocsHistoryModel).where(GenerateDocsHistoryModel.id == history_id))
            record = result.scalars().first()
            if not record:
                return None
            return {
                "id": record.id,
                "incoming_code": record.incoming_code,
                "styles_used": record.styles_used,
                "custom_style_used": record.custom_style_used,
                "ai_response": record.ai_response,
                "createdAT": record.createdAT
            }

    async def get_explain_history(self, history_id: str) -> dict | None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(ExplainHistoryModel).where(ExplainHistoryModel.id == history_id))
            record = result.scalars().first()
            if not record:
                return None
            return {
                "id": record.id,
                "incoming_code": record.incoming_code,
                "styles_used": record.styles_used,
                "custom_style_used": record.custom_style_used,
                "ai_response": record.ai_response,
                "createdAT": record.createdAT
            }

    async def get_all_docs_history(self, user_id: str, file_id: str = None) -> list:
        async with AsyncSessionLocal() as session:
            stmt = select(GenerateDocsHistoryModel.id, GenerateDocsHistoryModel.incoming_code, GenerateDocsHistoryModel.createdAT).where(GenerateDocsHistoryModel.user_id == user_id)
            if file_id:
                stmt = stmt.where(GenerateDocsHistoryModel.file_id == file_id)
            
            result = await session.execute(stmt.order_by(GenerateDocsHistoryModel.createdAT.desc()))
            records = result.all()
            return [{"id": str(r.id), "incoming_code": r.incoming_code, "createdAT": r.createdAT} for r in records]

    async def get_all_explain_history(self, user_id: str, file_id: str = None) -> list:
        async with AsyncSessionLocal() as session:
            stmt = select(ExplainHistoryModel.id, ExplainHistoryModel.incoming_code, ExplainHistoryModel.createdAT).where(ExplainHistoryModel.user_id == user_id)
            if file_id:
                stmt = stmt.where(ExplainHistoryModel.file_id == file_id)
                
            result = await session.execute(stmt.order_by(ExplainHistoryModel.createdAT.desc()))
            records = result.all()
            return [{"id": str(r.id), "incoming_code": r.incoming_code, "createdAT": r.createdAT} for r in records]

    async def clear_all_history(self) -> dict:
        async with AsyncSessionLocal() as session:
            await session.execute(delete(GenerateDocsHistoryModel))
            await session.execute(delete(ExplainHistoryModel))
            await session.commit()
            return {"status": "success", "message": "All database history safely destroyed."}

    async def delete_docs_history(self, history_id: str) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(GenerateDocsHistoryModel).where(GenerateDocsHistoryModel.id == history_id)
            )
            await session.commit()
            return result.rowcount > 0

    async def delete_explain_history(self, history_id: str) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(ExplainHistoryModel).where(ExplainHistoryModel.id == history_id)
            )
            await session.commit()
            return result.rowcount > 0
