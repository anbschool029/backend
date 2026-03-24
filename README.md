# 🚀 VIBE: AI-Powered Hexagonal Backend

Welcome to the core engine of **VIBE** (Vibrant Intelligent Build Environment). This backend is a high-performance API engineered with **FastAPI** and designed using the **Hexagonal Architecture (Ports and Adapters)** pattern. It specializes in automated code documentation, intelligent chat interfaces, and collaborative workspace management.

---

## 🛠️ Overview & Purpose

The primary goal of this backend is to bridge the gap between complex codebases and human-readable documentation. By leveraging cutting-edge LLMs (via Groq), it transforms raw code into professional docstrings or comprehensive Markdown guides instantly.

### Core Value Propositions:
- **Instant Documentation**: Convert logic into JSDoc, Google Python Docstrings, etc.
- **Deep Explanations**: Breakdown complex algorithms for non-technical founders.
- **Scalable Architecture**: Decoupled design allows for easy swapping of LLM providers or database engines.
- **Identity & Analytics**: TripCode-based identity for tracking contributions and activity.

---

## 🏗️ Technical Architecture: Hexagonal Design

This project avoids "spaghetti code" by strictly separating business logic from technical implementation details.

### 1. Domain Layer (The Brain)
- **Path**: `app/domain/`
- **Purpose**: Contains the core business logic (`services.py`) and data structure definitions (`schemas.py`).
- **Logic**: It only knows *what* to do (e.g., "build a prompt for documentation"), not *how* to talk to a database or an AI.

### 2. Ports (The Interfaces)
- **Path**: `app/ports/`
- **Purpose**: Defines the "contracts" that the Domain layer uses.
- **Example**: `LLMPort` defines that any AI client must have a `generate_text` method.

### 3. Adapters (The Implementation)
- **Path**: `app/adapters/`
- **Purpose**: Real-world implementations of the Ports.
- **Examples**: 
    - `groq_adapter.py`: Connects to the Groq Cloud API.
    - `database.py`: Handles SQLite persistence using SQLAlchemy.
    - `sqlite_history_adapter.py`: Manages long-term storage of generated docs.

---

## 🚀 Getting Started

### 📋 Prerequisites
- **Python**: version 3.14 or higher.
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (Extremely fast Python package installer and resolver).

### 🛠️ Local Setup
1. **Initialize Environment**:
   ```bash
   cp .env.example .env # Ensure you fill in your GROQ_API_KEY
   ```
2. **Install Dependencies**:
   ```bash
   uv sync
   ```
3. **Launch Project**:
   ```bash
   make dev
   ```
   *The server will start at `http://localhost:8000` with auto-reload enabled.*

---

## 🚢 Deployment & Production

### Vercel (Recommended)
This codebase is optimized for serverless environments. To deploy:
1. Connect your GitHub repository to Vercel.
2. Set Environment Variables (`GROQ_API_KEY`, etc.) in the Vercel dashboard.
3. Vercel will auto-detect the FastAPI configuration via `vercel.json`.

### Manual Deployment
Run the production server using Uvicorn:
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📖 API Reference (Swagger UI)

Interactive documentation is available at `/docs`.

### 🔐 Multi-Session Identity (Auth)
VIBE uses a unique **TripCode** system to identify users without requiring heavy passwords.

#### `POST /api/auth/login`
- **Purpose**: Generates a deterministic ID and TripCode based on a secret key.
- **Input**:
  ```json
  {
    "username": "DevQueen",
    "secret_key": "mySecret123"
  }
  ```
- **Output**: `user_id`, `tripcode`, and `session_token`.

#### `POST /api/auth/heartbeat-off`
- **Purpose**: Marks a user as offline immediately.
- **Input**: `{"user_id": "..."}`

---

### 📝 AI Engines (Docs & Chat)

#### `POST /api/documentation-generator`
- **Purpose**: The flagship feature. Generates code documentation or step-by-step explanations.
- **Input**:
  ```json
  {
    "code": "function sum(a, b) { return a + b; }",
    "styles": ["Professional", "Concise"],
    "mode": "code_docs", // Use "explain" for rich markdown breakdown
    "user_id": "your-uuid",
    "project_id": "optional-uuid",
    "file_id": "optional-uuid"
  }
  ```

#### `POST /api/chat`
- **Purpose**: Direct stream-like interface for AI interaction.
- **Input**: `{"messages": [{"role": "user", "content": "Explain React hooks"}]}`

---

### 📁 Workspace Management
Complete CRUD operations for managing Projects and Files with **Cascading Deletes**.

- **Projects**: `GET /api/workspace/projects/{user_id}`, `POST /api/workspace/projects`, `DELETE /api/workspace/projects/{project_id}`
- **Files**: `GET /api/workspace/files/{project_id}`, `POST /api/workspace/files`, `DELETE /api/workspace/files/{file_id}`

---

## 📊 Leaderboard & Analytics
#### `GET /api/leaderboard`
- **Returns**: A real-time list of active users, their tripcodes, and their contribution counts (docs generated vs code explained).

---

## 🛠️ Tech Stack
- **Web Framework**: FastAPI core.
- **AI Integration**: Groq Cloud SDK (Llama 3 / Mistral Support).
- **ORM**: SQLAlchemy 2.0 (Asynchronous).
- **Database**: SQLite (aiosqlite).
- **Tooling**: `uv` for package management, `Makefile` for developer experience.

---
*Developed with focus on logic transparency and code elegance.*
