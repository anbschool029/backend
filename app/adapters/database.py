import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, func

# Scalable integration pattern using SQLite and aiosqlite for proper async I/O
DATABASE_URL = "sqlite+aiosqlite:///./docs.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class AuditMixin:
    """
    Mixin containing Full Audit Tracking explicitly defining nullable and indexing for all attributes natively.
    """
    createBy: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    createdAT: Mapped[Optional[datetime]] = mapped_column(DateTime, default=func.now(), nullable=True, index=True)
    editedBy: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    editedAt: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    updateBy: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    updateAt: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=func.now(), index=True)

class ProjectModel(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

class FileModel(Base):
    __tablename__ = "files"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    project_id: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

class GenerateDocsHistoryModel(AuditMixin, Base):
    __tablename__ = "generate_docs_history"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    incoming_code: Mapped[str] = mapped_column(Text, index=True)
    styles_used: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    custom_style_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True, index=True)
    ai_response: Mapped[str] = mapped_column(Text, index=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    file_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)

class ExplainHistoryModel(AuditMixin, Base):
    __tablename__ = "explain_history"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    incoming_code: Mapped[str] = mapped_column(Text, index=True)
    styles_used: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    custom_style_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True, index=True)
    ai_response: Mapped[str] = mapped_column(Text, index=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    file_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)

class UserModel(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    nickname: Mapped[str] = mapped_column(String, index=True)
    tripcode: Mapped[str] = mapped_column(String, index=True)
    last_active: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), index=True)

async def init_db():
    """Initializes the Sqlite Data file asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
