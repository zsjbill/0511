"""
M5: Report Scheduler — Scheduled report generation (daily 9:00 / weekly Monday).
"""
import asyncio
import logging
from datetime import datetime, time

logger = logging.getLogger(__name__)


class ReportScheduler:
    """Schedule automatic report generation."""

    def __init__(self) -> None:
        self.jobs: list[dict] = [
            {"type": "daily", "time": time(9, 0)},
            {"type": "weekly", "day_of_week": 0, "time": time(9, 0)},  # Monday
        ]

    async def start(self) -> None:
        """Start the scheduler loop."""
        logger.info("Report scheduler started with %d jobs", len(self.jobs))
        while True:
            now = datetime.now()
            for job in self.jobs:
                if self._should_run(job, now):
                    await self._trigger(job["type"])
            await asyncio.sleep(60)  # check every minute

    def _should_run(self, job: dict, now: datetime) -> bool:
        job_time = job["time"]
        if now.hour != job_time.hour or now.minute != job_time.minute:
            return False
        if job.get("day_of_week") is not None:
            if now.weekday() != job["day_of_week"]:
                return False
        return True

    async def _trigger(self, report_type: str) -> None:
        """Trigger a report generation job."""
        logger.info("Triggering %s report generation", report_type)
        # TODO: call ReportService.generate()
