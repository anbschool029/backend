from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import chat, documentation, history, auth, leaderboard, management, workspace
from app.adapters.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup SQLite tables completely fully automatically!
    await init_db()
    yield

app = FastAPI(
    title="VIBE Hexagonal Backend",
    description="Refactored using Ports and Adapters concept for high scalability and beginner-friendliness.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect Routes (Primary Driving Adapters)
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(documentation.router, prefix="/api/documentation-generator", tags=["Documentation"])
app.include_router(history.router, prefix="/api/history", tags=["History"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["Leaderboard"])
app.include_router(management.router, prefix="/api/admin", tags=["Admin"])
app.include_router(workspace.router, prefix="/api/workspace", tags=["Workspace"])
