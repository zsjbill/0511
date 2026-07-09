import asyncio, logging
from sqlalchemy import select
from src.common.database import EnterpriseSessionLocal
from src.common.models_enterprise import ComplaintFeedback

logger = logging.getLogger(__name__)

_pending_tasks: list[dict] = []

async def scan_tasks():
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
    return _pending_tasks

async def start_scanner(interval_seconds: int = 60):
    while True:
        try:
            await scan_tasks()
        except Exception as e:
            logger.error(f"Scanner error: {e}")
        await asyncio.sleep(interval_seconds)
