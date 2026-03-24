from fastapi import APIRouter, HTTPException
from sqlalchemy.future import select
from sqlalchemy import delete, update
from app.adapters.database import (
    AsyncSessionLocal, ProjectModel, FileModel,
    GenerateDocsHistoryModel, ExplainHistoryModel
)
from pydantic import BaseModel

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    user_id: str

class ProjectRename(BaseModel):
    name: str

class FileCreate(BaseModel):
    name: str
    project_id: str

class FileRename(BaseModel):
    name: str


# ── Projects ─────────────────────────────────────────────────────────────────

@router.get("/projects/{user_id}")
async def get_projects(user_id: str):
    async with AsyncSessionLocal() as session:
        stmt = select(ProjectModel).where(ProjectModel.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().all()

@router.post("/projects")
async def create_project(req: ProjectCreate):
    async with AsyncSessionLocal() as session:
        project = ProjectModel(name=req.name, user_id=req.user_id)
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project

@router.patch("/projects/{project_id}")
async def rename_project(project_id: str, req: ProjectRename):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ProjectModel).where(ProjectModel.id == project_id))
        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await session.execute(
            update(ProjectModel).where(ProjectModel.id == project_id).values(name=req.name)
        )
        await session.commit()
        return {"id": project_id, "name": req.name}

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """
    Cascading delete: removes the project, all its files,
    and all docs/explain history tied to those files.
    """
    async with AsyncSessionLocal() as session:
        # 1. Find all files belonging to this project
        files_result = await session.execute(
            select(FileModel.id).where(FileModel.project_id == project_id)
        )
        file_ids = [row[0] for row in files_result.all()]

        # 2. Delete all history for each file
        if file_ids:
            await session.execute(
                delete(GenerateDocsHistoryModel).where(GenerateDocsHistoryModel.file_id.in_(file_ids))
            )
            await session.execute(
                delete(ExplainHistoryModel).where(ExplainHistoryModel.file_id.in_(file_ids))
            )

        # 3. Also delete any history scoped to project_id directly (no file)
        await session.execute(
            delete(GenerateDocsHistoryModel).where(GenerateDocsHistoryModel.project_id == project_id)
        )
        await session.execute(
            delete(ExplainHistoryModel).where(ExplainHistoryModel.project_id == project_id)
        )

        # 4. Delete all files
        await session.execute(delete(FileModel).where(FileModel.project_id == project_id))

        # 5. Delete the project itself
        result = await session.execute(
            delete(ProjectModel).where(ProjectModel.id == project_id)
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Project not found")

        await session.commit()
        return {"status": "deleted", "project_id": project_id}


# ── Files ─────────────────────────────────────────────────────────────────────

@router.get("/files/{project_id}")
async def get_files(project_id: str):
    async with AsyncSessionLocal() as session:
        stmt = select(FileModel).where(FileModel.project_id == project_id)
        result = await session.execute(stmt)
        return result.scalars().all()

@router.post("/files")
async def create_file(req: FileCreate):
    async with AsyncSessionLocal() as session:
        file = FileModel(name=req.name, project_id=req.project_id)
        session.add(file)
        await session.commit()
        await session.refresh(file)
        return file

@router.patch("/files/{file_id}")
async def rename_file(file_id: str, req: FileRename):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(FileModel).where(FileModel.id == file_id))
        file = result.scalars().first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        await session.execute(
            update(FileModel).where(FileModel.id == file_id).values(name=req.name)
        )
        await session.commit()
        return {"id": file_id, "name": req.name}

@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """
    Cascading delete: removes the file and all its
    associated docs and explain history records.
    """
    async with AsyncSessionLocal() as session:
        # 1. Delete all history tied to this file
        await session.execute(
            delete(GenerateDocsHistoryModel).where(GenerateDocsHistoryModel.file_id == file_id)
        )
        await session.execute(
            delete(ExplainHistoryModel).where(ExplainHistoryModel.file_id == file_id)
        )

        # 2. Delete the file itself
        result = await session.execute(
            delete(FileModel).where(FileModel.id == file_id)
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="File not found")

        await session.commit()
        return {"status": "deleted", "file_id": file_id}
