"""
M4: Leave Workflow — Full-chain leave approval.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


class LeaveWorkflow:
    """Handle student leave application workflow."""

    async def submit(self, student_id: int, reason: str, days: int) -> dict[str, Any]:
        """Submit leave request → validate → notify approver."""
        # Step 1: Validate
        if days <= 0:
            return {"status": "rejected", "message": "请假天数必须大于0"}

        # Step 2: Check remaining leave quota (TODO: query external system)
        quota_ok = await self._check_quota(student_id, days)
        if not quota_ok:
            return {"status": "rejected", "message": "剩余假期不足"}

        # Step 3: Create leave record (TODO: DB)
        leave_id = await self._create_leave(student_id, reason, days)

        # Step 4: Notify approver (TODO: push notification)
        await self._notify_approver(student_id, leave_id)

        return {"status": "submitted", "leave_id": leave_id, "message": "请假申请已提交，等待审批"}

    async def _check_quota(self, student_id: int, days: int) -> bool:
        # TODO: query external system
        return True

    async def _create_leave(self, student_id: int, reason: str, days: int) -> int:
        # TODO: DB insert
        return 1

    async def _notify_approver(self, student_id: int, leave_id: int) -> None:
        # TODO: send notification
        pass
