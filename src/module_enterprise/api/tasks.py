"""
企业管理模块 - 待办任务与指令执行 API。

提供待办任务查询、手动扫描触发、任务确认（ack）以及
自然语言指令执行（更新投诉/客户状态）等功能。
"""
import logging
from fastapi import APIRouter
from src.module_enterprise.pdcmodel.schemas import APIResponse, InstructionRequest
from src.module_enterprise.service.instruction import execute_instruction as handle_instruction
from src.module_enterprise.service.task_scanner import get_pending_tasks, scan_tasks

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/enterprise/tasks", tags=["Enterprise - Tasks"])


@router.get("/pending", response_model=APIResponse, summary="获取待办任务列表", description="返回当前缓存的待办任务列表，包含任务类型、内容摘要、提交时间和状态")
async def pending_tasks():
    """获取当前所有待办任务列表。

    从内存中读取由后台扫描器维护的待办任务列表，
    返回任务 ID、类型（如投诉反馈）、内容摘要、提交时间、状态等信息。

    Returns:
        包含待办任务列表及数量的 APIResponse
    """
    tasks = get_pending_tasks()
    return APIResponse(data={"tasks": tasks, "count": len(tasks)})


@router.post("/scan", response_model=APIResponse, summary="手动扫描待办任务", description="手动触发扫描 complaint_feedback 表，更新待办任务缓存")
async def trigger_scan():
    """手动触发待办任务扫描。

    立即扫描 complaint_feedback 表中 status != '已跟进' 的记录，
    更新全局待办任务列表缓存，并返回扫描结果。

    Returns:
        包含扫描后待办任务列表及数量的 APIResponse
    """
    await scan_tasks()
    tasks = get_pending_tasks()
    return APIResponse(data={"tasks": tasks, "count": len(tasks)}, message="Scan completed")


@router.post("/{task_id}/ack", response_model=APIResponse, summary="确认待办任务", description="标记指定 ID 的待办任务为已确认处理")
async def ack_task(task_id: int):
    """确认（acknowledge）一条待办任务。

    标记指定 ID 的任务为已确认处理状态。

    Args:
        task_id: 待办任务的 ID

    Returns:
        确认成功的 APIResponse
    """
    return APIResponse(message=f"Task {task_id} acknowledged")


# ── Instruction Router (natural language to CRUD) 自然语言指令路由 ─────

instruction_router = APIRouter(prefix="/api/v1/enterprise/instruction", tags=["Enterprise - Instruction"])


@instruction_router.post("/execute", response_model=APIResponse, summary="执行自然语言指令", description="接收自然语言指令，解析为 CRUD 操作并执行（如更新投诉状态、客户状态等）")
async def execute_instruction_endpoint(request: InstructionRequest):
    """执行自然语言指令。

    接收用户用自然语言描述的指令（如"将张三的投诉状态改为已跟进"），
    通过 LLM 解析为结构化的 CRUD 操作，并在数据库中执行。

    Args:
        request: 包含自然语言指令的请求体

    Returns:
        包含解析结果和执行结果的 APIResponse
    """
    try:
        result = await handle_instruction(request.instruction)
        return APIResponse(data=result)
    except Exception as e:
        logger.exception("Instruction execution failed")
        return APIResponse(code=500, message=str(e))
