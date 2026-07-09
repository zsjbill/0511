"""
M3: Onboard Guide — New employee onboarding RAG.
"""
import logging
from typing import Any

from src.common.vector_store import vector_store

logger = logging.getLogger(__name__)


class OnboardGuide:
    """Generate personalized onboarding guides for new employees."""

    async def generate(self, employee_id: int) -> dict[str, Any]:
        """Generate onboarding guide based on role and department."""
        # TODO: retrieve employee info, then RAG search onboarding docs
        sections = await self._get_onboarding_sections("技术部")
        return {
            "employee_id": employee_id,
            "sections": sections,
            "message": f"欢迎加入！以下是你的入职指南（共{len(sections)}项）。",
        }

    async def _get_onboarding_sections(self, department: str) -> list[dict[str, Any]]:
        """Retrieve relevant onboarding sections."""
        # TODO: RAG search in company policy docs
        return [
            {"title": "公司文化与价值观", "content": "..."},
            {"title": "IT设备与账号", "content": "..."},
            {"title": "部门介绍与团队", "content": "..."},
        ]
