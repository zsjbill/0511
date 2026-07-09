"""
M4: Complaint Summarizer — Intelligent complaint summarization.
"""
import logging

from src.common.llm_client import llm_client

logger = logging.getLogger(__name__)


class ComplaintSummarizer:
    """Generate structured summaries from student complaint conversations."""

    async def summarize(self, conversation: list[dict]) -> str:
        """Summarize a complaint conversation."""
        convo_text = "\n".join(f"{m.get('role', '?')}: {m.get('content', '')}" for m in conversation)

        prompt = f"""请将以下投诉对话总结为一段简洁的摘要（不超过150字），包含：
1. 投诉核心问题
2. 学生的核心诉求
3. 建议处理方向

对话：
{convo_text}"""

        summary = await llm_client.chat([
            {"role": "system", "content": "你是一个专业的投诉处理助理。"},
            {"role": "user", "content": prompt},
        ])
        return summary
