"""
M4: Student Assistant — Core business orchestration.
"""
import logging
from typing import Any

from src.common.llm_client import llm_client
from src.common.schemas import RiskDetectionRequest, RiskDetectionResponse, RiskLevel
from src.module_m4_student_assistant.risk_monitor import RiskMonitor
from src.module_m4_student_assistant.life_knowledge import LifeKnowledge
from src.module_m4_student_assistant.marketing_generator import MarketingGenerator
from src.module_m4_student_assistant.complaint_summarizer import ComplaintSummarizer
from src.module_m4_student_assistant.leave_workflow import LeaveWorkflow

logger = logging.getLogger(__name__)


class StudentService:
    """Orchestrates all student assistant features."""

    def __init__(self) -> None:
        self.risk_monitor = RiskMonitor()
        self.life_knowledge = LifeKnowledge()
        self.marketing_generator = MarketingGenerator()
        self.complaint_summarizer = ComplaintSummarizer()
        self.leave_workflow = LeaveWorkflow()

    async def detect_risk(self, request: RiskDetectionRequest) -> RiskDetectionResponse:
        return await self.risk_monitor.analyze(request)

    async def query_life_knowledge(self, student_id: int, query: str) -> dict[str, Any]:
        return await self.life_knowledge.search(student_id, query)

    async def handle_leave(self, student_id: int, reason: str, days: int) -> dict[str, Any]:
        return await self.leave_workflow.submit(student_id, reason, days)

    async def summarize_complaint(self, conversation: list[dict]) -> str:
        return await self.complaint_summarizer.summarize(conversation)

    async def generate_marketing(self, student_profile: dict) -> str:
        return await self.marketing_generator.generate(student_profile)


student_service = StudentService()
