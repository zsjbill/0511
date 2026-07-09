"""
M5: Report Generator — Generate reports in PDF/HTML formats.
"""
import logging
from typing import Any

from src.common.llm_client import llm_client

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate report content using LLM + templates."""

    async def generate(self, report_type: str, data: dict[str, Any]) -> str:
        """Generate report content from aggregated data."""
        prompt = f"""请根据以下数据生成一份{report_type}报告摘要（Markdown格式）：

数据：
{data}

要求：简洁专业，突出关键指标和变化趋势。"""

        content = await llm_client.chat([
            {"role": "system", "content": "你是一个专业的运营报告生成助理。"},
            {"role": "user", "content": prompt},
        ])
        return content

    async def export_pdf(self, content: str) -> bytes:
        """Export report as PDF."""
        # TODO: use WeasyPrint / ReportLab
        logger.info("PDF export not yet implemented")
        return b""

    async def export_html(self, content: str) -> str:
        """Export report as HTML."""
        # TODO: use Jinja2 template
        return f"<html><body>{content}</body></html>"
