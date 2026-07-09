"""
AI-CSM-2026 FastAPI Application Entry Point.

Registers all module routers and lifecycle hooks.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.logging_config import setup_logging
from src.common.database import close_db

# Enterprise module routers
from src.module_enterprise.api_crud import router as enterprise_crud_router
from src.module_enterprise.api_nl2sql import router as enterprise_nl2sql_router
from src.module_enterprise.api_tasks import router as enterprise_tasks_router
from src.module_enterprise.api_tasks import instruction_router as enterprise_instruction_router

# Student module routers
from src.module_student.api_crud import router as student_crud_router
from src.module_student.api_application import router as student_approval_router
from src.module_student.api_sync import router as student_sync_router
from src.module_student.api_kb import router as student_kb_router
from src.module_student.api_ai import router as student_ai_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    setup_logging()
    # Start background scanners
    import asyncio
    try:
        from src.module_enterprise.task_scanner import start_scanner
        asyncio.create_task(start_scanner())
    except Exception:
        pass
    try:
        from src.module_student.sync_service import start_scheduler
        asyncio.create_task(start_scheduler())
    except Exception:
        pass
    yield
    await close_db()


app = FastAPI(
    title="AI-CSM-2026",
    description="智能客服与学生管理系统",
    version="2.0.0",
    lifespan=lifespan,
)

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Register Routers ----
app.include_router(enterprise_crud_router)
app.include_router(enterprise_nl2sql_router)
app.include_router(enterprise_tasks_router)
app.include_router(enterprise_instruction_router)
app.include_router(student_crud_router)
app.include_router(student_sync_router)
app.include_router(student_kb_router)
app.include_router(student_ai_router)
app.include_router(student_approval_router)

# ---- Health Check ----
@app.get("/health", tags=["System"])
async def health_check() -> dict:
    return {"status": "healthy", "service": "AI-CSM-2026", "databases": ["enterprise_assistant", "student_assistant"]}

# ---- Static files (optional frontend) ----
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
