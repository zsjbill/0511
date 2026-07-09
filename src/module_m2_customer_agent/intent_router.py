"""
M2: Intent Router — 7-intent classification using LLM.
"""
import logging
from typing import Any

from src.common.llm_client import llm_client
from src.common.schemas import IntentType

logger = logging.getLogger(__name__)

INTENT_EXAMPLES: dict[IntentType, list[str]] = {
    IntentType.COURSE_INQUIRY: ["有什么课程", "留学方案", "推荐国家"],
    IntentType.REGISTRATION: ["报名", "参加活动", "预约"],
    IntentType.PRICE_INQUIRY: ["多少钱", "价格", "优惠", "分期"],
    IntentType.COMPLAINT: ["投诉", "不满意", "退款", "差评"],
    IntentType.CHITCHAT: ["你好", "天气", "你是机器人吗"],
    IntentType.COMPANY_INFO: ["你们公司", "靠谱吗", "成立多久"],
    IntentType.OTHER: [],
}


class IntentRouter:
    """Classify user message into one of 7 intents."""

    async def classify(self, message: str) -> tuple[IntentType, float]:
        """
        Use LLM for intent classification.
        Returns (intent, confidence).
        """
        prompt = self._build_classification_prompt(message)
        try:
            result = await llm_client.chat_json([
                {"role": "system", "content": prompt},
                {"role": "user", "content": message},
            ])
            intent_str = result.get("intent", "其他")
            confidence = float(result.get("confidence", 0.5))
            intent = IntentType(intent_str) if intent_str in IntentType._value2member_map_ else IntentType.OTHER
            return intent, confidence
        except Exception:
            logger.exception("Intent classification failed, fallback to OTHER")
            return IntentType.OTHER, 0.3

    def _build_classification_prompt(self, _message: str) -> str:
        examples_lines = []
        for intent, examples in INTENT_EXAMPLES.items():
            if examples:
                examples_lines.append(f"  - {intent.value}: {', '.join(examples)}")
        return f"""将用户消息分类到以下意图之一：
{chr(10).join(examples_lines)}

输出JSON格式：{{"intent": "意图名称", "confidence": 0.0-1.0}}"""
