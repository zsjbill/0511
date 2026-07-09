from fastapi import APIRouter
from src.common.schemas_enterprise import APIResponse, InstructionRequest
from src.module_enterprise.instruction_handler import execute_instruction
from src.module_enterprise.task_scanner import get_pending_tasks, scan_tasks

router = APIRouter(prefix="/api/v1/enterprise/tasks", tags=["Enterprise - Tasks"])

@router.get("/pending", response_model=APIResponse)
async def pending_tasks():
    tasks = get_pending_tasks()
    return APIResponse(data={"tasks": tasks, "count": len(tasks)})

@router.post("/scan", response_model=APIResponse)
async def trigger_scan():
    await scan_tasks()
    tasks = get_pending_tasks()
    return APIResponse(data={"tasks": tasks, "count": len(tasks)}, message="Scan completed")

@router.post("/{task_id}/ack", response_model=APIResponse)
async def ack_task(task_id: int):
    return APIResponse(message=f"Task {task_id} acknowledged")


# ── Instruction Router (natural language → CRUD) ──────────────────────

instruction_router = APIRouter(prefix="/api/v1/enterprise/instruction", tags=["Enterprise - Instruction"])


@instruction_router.post("/execute", response_model=APIResponse)
async def execute_instruction_endpoint(request: InstructionRequest):
    try:
        result = await execute_instruction(request.instruction)
        return APIResponse(data=result)
    except Exception as e:
        logger.exception("Instruction execution failed")
        return APIResponse(code=500, message=str(e))
