"""学生端数据同步 API 端点。

提供校园教务系统 DDL 同步、CRM 进度同步、
以及同步状态查询接口。
"""

from fastapi import APIRouter
from src.module_student.pdcmodel.schemas import APIResponse
from src.module_student.service.sync import run_sync, get_sync_status

router = APIRouter(prefix="/api/v1/student/sync", tags=["Student - Sync"])

@router.post("/campus/ddl", response_model=APIResponse,
             summary="同步校园 DDL", description="从校园教务系统同步教学计划/DDL 数据（campus_ddl）。")
async def sync_campus_ddl():
    """同步校园教务系统的 DDL（教学计划/截止日期）数据。

    从外部教务系统拉取最新教学计划安排，
    更新到本地 student_admin_services 表中。
    """
    result = await run_sync("campus_ddl")
    return APIResponse(data=result, message="Campus DDL sync completed")

@router.post("/crm/progress", response_model=APIResponse,
             summary="同步 CRM 进度", description="从 CRM 系统同步学生学习/服务进度数据（crm_progress）。")
async def sync_crm_progress():
    """同步 CRM 系统中的学生学习/服务进度数据。

    从外部 CRM 系统拉取学生跟进记录和进度信息，
    更新到本地数据库。
    """
    result = await run_sync("crm_progress")
    return APIResponse(data=result, message="CRM progress sync completed")

@router.get("/status", response_model=APIResponse,
            summary="查询同步状态", description="查询各同步任务的最新执行状态。")
async def sync_status():
    """查询所有同步任务的最近一次同步状态。"""
    return APIResponse(data=get_sync_status())
