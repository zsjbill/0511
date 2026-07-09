"""
M3: Enterprise Assistant — Core business orchestration.
"""
import logging
from typing import Any

from src.common.llm_client import llm_client
from src.common.schemas import NL2SQLRequest, NL2SQLResponse
from src.module_m3_enterprise_assistant.nl2sql_engine import NL2SQLEngine
from src.module_m3_enterprise_assistant.org_query import OrgQuery
from src.module_m3_enterprise_assistant.onboard_guide import OnboardGuide
from src.module_m3_enterprise_assistant.task_trigger import TaskTrigger

logger = logging.getLogger(__name__)


class EnterpriseService:
    """Orchestrates enterprise assistant features."""

    def __init__(self) -> None:
        self.nl2sql_engine = NL2SQLEngine()
        self.org_query = OrgQuery()
        self.onboard_guide = OnboardGuide()
        self.task_trigger = TaskTrigger()

    async def nl2sql(self, request: NL2SQLRequest) -> NL2SQLResponse:
        return await self.nl2sql_engine.execute(request)

    async def query_org(self, employee_id: int) -> dict[str, Any]:
        return await self.org_query.lookup(employee_id)

    async def get_onboard_guide(self, employee_id: int) -> dict[str, Any]:
        return await self.onboard_guide.generate(employee_id)

    async def check_pending_tasks(self, user_id: int) -> list[dict[str, Any]]:
        return await self.task_trigger.get_pending(user_id)


enterprise_service = EnterpriseService()
