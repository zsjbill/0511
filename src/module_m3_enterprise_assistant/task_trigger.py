"""
M3: Task Trigger — Proactive pending task push.
"""
import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


class TaskTrigger:
    """Periodically check and push pending tasks to users."""

    async def get_pending(self, user_id: int) -> list[dict[str, Any]]:
        """Fetch pending tasks for a user."""
        # TODO: query from task/workflow system
        return [
            {"id": 1, "type": "审批", "title": "张三的请假申请", "urgency": "normal"},
        ]

    async def start_scheduler(self, interval_seconds: int = 300) -> None:
        """Start background task scheduler."""
        logger.info("Task scheduler started (interval=%ds)", interval_seconds)
        while True:
            try:
                # TODO: query all users with pending tasks and push notifications
                await asyncio.sleep(interval_seconds)
            except Exception:
                logger.exception("Scheduler error")
