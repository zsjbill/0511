"""
M2: Registration Handler — Activity registration business logic.
"""
import logging
from typing import Any, Optional

from src.common.schemas import RegistrationRequest, RegistrationResponse

logger = logging.getLogger(__name__)


class RegistrationHandler:
    """Handle activity registration workflow."""

    async def process(self, request: RegistrationRequest) -> RegistrationResponse:
        """Full registration flow: validate → create → notify."""
        # Validate
        if not request.customer_id or not request.activity_name:
            return RegistrationResponse(
                registration_id=0,
                status="failed",
                message="缺少必要信息（客户ID / 活动名称）",
            )

        # Create registration (TODO: persist)
        registration_id = await self._create_registration(request)

        # Send notification (TODO)
        await self._notify(request.customer_id, request.activity_name)

        return RegistrationResponse(
            registration_id=registration_id,
            status="confirmed",
            message=f"已成功报名「{request.activity_name}」，我们会尽快与您联系！",
        )

    async def _create_registration(self, request: RegistrationRequest) -> int:
        # TODO: DB insert
        return 1

    async def _notify(self, customer_id: int, activity_name: str) -> None:
        # TODO: send SMS / WeChat notification
        pass
