"""
企业管理模块 - 待办任务扫描器。

定期扫描 complaint_feedback 表中未跟进的投诉反馈记录，
将其作为待办任务缓存到内存中，供 API 查询使用。
"""
import asyncio, logging
from sqlalchemy import select
from src.common.database import EnterpriseSessionLocal
from src.common.models_enterprise import ComplaintFeedback

logger = logging.getLogger(__name__)

# 内存中缓存的待办任务列表
_pending_tasks: list[dict] = []


async def scan_tasks():
    """扫描数据库中的待办任务。

    查询 complaint_feedback 表中 status != '已跟进' 的记录，
    提取任务 ID、投诉类型、学生姓名、投诉内容摘要、提交时间等信息，
    更新全局待办任务列表缓存。
    """
    global _pending_tasks
    async with EnterpriseSessionLocal() as db:
        result = await db.execute(
            select(ComplaintFeedback).where(ComplaintFeedback.status != "已跟进")
        )
        items = result.scalars().all()
        _pending_tasks = [
            {
                "id": item.id,
                "type": "complaint_feedback",
                "content": f"{item.student_name}: {item.complaint_detail[:80]}...",
                "submitted_at": item.created_at.isoformat() if item.created_at else None,
                "link": f"/complaints/{item.id}",
                "status": item.status,
            }
            for item in items
        ]
    logger.info(f"Scanned: {len(_pending_tasks)} pending tasks found")


def get_pending_tasks() -> list[dict]:
    """获取当前缓存的待办任务列表。

    Returns:
        待办任务字典列表，每个任务包含 id、type、content、submitted_at、link、status
    """
    return _pending_tasks


async def start_scanner(interval_seconds: int = 60):
    """启动后台待办任务定时扫描器。

    每隔指定时间间隔（默认 60 秒）自动扫描 complaint_feedback 表，
    刷新内存中的待办任务列表。

    Args:
        interval_seconds: 扫描间隔时间（秒），默认 60 秒
    """
    while True:
        try:
            await scan_tasks()
        except Exception as e:
            logger.error(f"Scanner error: {e}")
        await asyncio.sleep(interval_seconds)
