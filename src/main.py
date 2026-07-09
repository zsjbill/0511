"""
AI-CSM-2026 FastAPI 应用入口。

注册所有模块路由、CORS 中间件、静态文件挂载及生命周期钩子。
"""
import sys, os
from pathlib import Path

# 确保项目根目录在 sys.path 中，以便正确导入各模块
_this_file = Path(__file__).resolve()
_project_root = _this_file.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.logging_config import setup_logging
from src.common.database import close_db

# Enterprise module routers 企业管理模块路由
from src.module_enterprise.api.crud import router as enterprise_crud_router
from src.module_enterprise.api.nl2sql import router as enterprise_nl2sql_router
from src.module_enterprise.api.tasks import router as enterprise_tasks_router
from src.module_enterprise.api.tasks import instruction_router as enterprise_instruction_router

# Student module routers 学生管理模块路由
from src.module_student.api.crud import router as student_crud_router
from src.module_student.api.application import router as student_approval_router
from src.module_student.api.sync import router as student_sync_router
from src.module_student.api.kb import router as student_kb_router
from src.module_student.api.ai import router as student_ai_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理，处理启动与关闭事件。

    启动时初始化日志配置，并启动后台任务扫描器；
    关闭时关闭数据库连接池。
    """
    setup_logging()
    # Start background scanners 启动后台任务扫描器
    import asyncio
    try:
        from src.module_enterprise.service.task_scanner import start_scanner
        asyncio.create_task(start_scanner())
    except Exception:
        pass
    try:
        from src.module_student.service.sync import start_scheduler
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

# ---- CORS 跨域配置 ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Register Routers 注册模块路由 ----
app.include_router(enterprise_crud_router)  # 企业管理 - CRUD 接口（客户、日报、投诉、成绩）
app.include_router(enterprise_nl2sql_router)  # 企业管理 - 自然语言转 SQL 查询接口
app.include_router(enterprise_tasks_router)  # 企业管理 - 待办任务接口
app.include_router(enterprise_instruction_router)  # 企业管理 - 自然语言指令执行接口
app.include_router(student_crud_router)  # 学生管理 - CRUD 接口
app.include_router(student_sync_router)  # 学生管理 - 数据同步接口
app.include_router(student_kb_router)  # 学生管理 - 知识库接口
app.include_router(student_ai_router)  # 学生管理 - AI 智能对话接口
app.include_router(student_approval_router)  # 学生管理 - 审批流程接口

# ---- Health Check 健康检查 ----
@app.get("/health", tags=["System"])
async def health_check() -> dict:
    """健康检查端点，返回服务运行状态及数据库连接信息。"""
    return {"status": "healthy", "service": "AI-CSM-2026", "databases": ["enterprise_assistant", "student_assistant"]}

# ---- Static files (optional frontend) 挂载前端静态文件 ----
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    os.chdir(str(_project_root))
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
