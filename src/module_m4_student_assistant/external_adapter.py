"""
M4: External Adapter — Integration with教务/CRM APIs.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ExternalAdapter:
    """Proxy for external system API calls (教务系统, CRM, etc.)."""

    async def get_student_info(self, student_id: int) -> dict[str, Any]:
        """Fetch student info from教务系统."""
        # TODO: HTTP call to external API
        logger.info("Fetching student info: %d", student_id)
        return {"id": student_id, "name": "示例学生", "stage": "语言班"}

    async def get_schedule(self, student_id: int) -> list[dict[str, Any]]:
        """Fetch course schedule from教务系统."""
        return []

    async def get_grades(self, student_id: int) -> list[dict[str, Any]]:
        """Fetch grades from教务系统."""
        return []

    async def get_crm_profile(self, student_id: int) -> dict[str, Any]:
        """Fetch CRM profile."""
        return {}
