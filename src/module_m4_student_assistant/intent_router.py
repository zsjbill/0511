"""
M4: Intent Router — 7 student scenario intents.
"""
import logging
from enum import Enum

from src.common.llm_client import llm_client

logger = logging.getLogger(__name__)


class StudentIntent(str, Enum):
    LEAVE = "请假申请"
    COMPLAINT = "投诉建议"
    LIFE = "海外生活咨询"
    COURSE = "课程相关"
    EXAM = "考试相关"
    MARKETING = "增值服务"
    OTHER = "其他"


class StudentIntentRouter:
    """Route student messages to the appropriate handler."""

    async def classify(self, message: str) -> tuple[StudentIntent, float]:
        try:
            result = await llm_client.chat_json([
                {"role": "system", "content": f"""将学生消息分类到以下意图之一：
{', '.join(i.value for i in StudentIntent)}

输出JSON格式：{{"intent": "...", "confidence": 0.0-1.0}}"""},
                {"role": "user", "content": message},
            ])
            intent = StudentIntent(result.get("intent", "其他"))
            confidence = float(result.get("confidence", 0.5))
            return intent, confidence
        except Exception:
            return StudentIntent.OTHER, 0.3
