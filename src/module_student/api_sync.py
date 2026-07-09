from fastapi import APIRouter
from src.common.schemas_student import APIResponse
from src.module_student.sync_service import run_sync, get_sync_status

router = APIRouter(prefix="/api/v1/student/sync", tags=["Student - Sync"])

@router.post("/campus/ddl", response_model=APIResponse)
async def sync_campus_ddl():
    result = await run_sync("campus_ddl")
    return APIResponse(data=result, message="Campus DDL sync completed")

@router.post("/crm/progress", response_model=APIResponse)
async def sync_crm_progress():
    result = await run_sync("crm_progress")
    return APIResponse(data=result, message="CRM progress sync completed")

@router.get("/status", response_model=APIResponse)
async def sync_status():
    return APIResponse(data=get_sync_status())
