"""
M5: Report Service — Report generation orchestration.
"""
import logging
from typing import Any

from src.common.schemas import ReportRequest, ReportResponse
from src.module_m5_report.data_aggregator import DataAggregator
from src.module_m5_report.report_generator import ReportGenerator
from src.module_m5_report.scheduler import ReportScheduler

logger = logging.getLogger(__name__)


class ReportService:
    """Orchestrate report generation workflow."""

    def __init__(self) -> None:
        self.aggregator = DataAggregator()
        self.generator = ReportGenerator()
        self.scheduler = ReportScheduler()

    async def generate(self, request: ReportRequest) -> ReportResponse:
        # Step 1: Aggregate data from multiple sources
        data = await self.aggregator.collect(request.report_type, request.date_range, request.metrics)

        # Step 2: Generate report content
        content = await self.generator.generate(request.report_type, data)

        # Step 3: Persist report
        report = await self._save_report(request.report_type, content)

        return report

    async def list_reports(self, report_type: str, page: int, page_size: int) -> dict[str, Any]:
        # TODO: query DB
        return {"items": [], "total": 0, "page": page, "page_size": page_size}

    async def get_report(self, report_id: int) -> dict[str, Any]:
        # TODO: query DB
        return {"id": report_id, "title": "", "content": ""}

    async def _save_report(self, report_type: str, content: str) -> ReportResponse:
        # TODO: DB insert
        import datetime
        return ReportResponse(
            report_id=1,
            title=f"{report_type}_report",
            content=content,
            generated_at=datetime.datetime.now(),
        )


report_service = ReportService()
