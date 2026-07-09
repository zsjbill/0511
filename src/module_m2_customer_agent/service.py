"""
M2: Customer Agent — Core dialogue service.
"""
import logging
from typing import Any

from src.common.llm_client import llm_client
from src.common.schemas import ChatRequest, ChatResponse, IntentType
from src.module_m2_customer_agent.intent_router import IntentRouter
from src.module_m2_customer_agent.rag_engine import RAGEngine

logger = logging.getLogger(__name__)


class CustomerAgentService:
    """Orchestrates customer dialogue: intent routing → RAG → response."""

    def __init__(self) -> None:
        self.intent_router = IntentRouter()
        self.rag_engine = RAGEngine()

    async def chat(self, request: ChatRequest) -> ChatResponse:
        # Step 1: Classify intent
        intent, confidence = await self.intent_router.classify(request.message)

        # Step 2: Retrieve relevant knowledge if needed
        context: list[dict[str, Any]] = []
        if intent in (IntentType.COURSE_INQUIRY, IntentType.COMPANY_INFO, IntentType.PRICE_INQUIRY):
            context = await self.rag_engine.search(request.message)

        # Step 3: Build prompt and generate response
        messages = self._build_messages(request.message, intent, context)
        reply = await llm_client.chat(messages)

        # Step 4: Generate follow-up suggestions
        suggestions = self._generate_suggestions(intent)

        return ChatResponse(
            reply=reply,
            intent=intent,
            confidence=confidence,
            suggestions=suggestions,
            actions=[],
        )

    def _build_messages(self, user_message: str, intent: IntentType, context: list[dict]) -> list[dict[str, str]]:
        system_prompt = "你是一个年轻活泼的留学咨询客服'小智'，帮助用户解答留学相关问题。"
        context_text = "\n".join(c.get("content", "") for c in context[:3])
        if context_text:
            system_prompt += f"\n\n参考知识：\n{context_text}"

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

    def _generate_suggestions(self, intent: IntentType) -> list[str]:
        suggestions_map = {
            IntentType.COURSE_INQUIRY: ["了解课程详情", "预约试听课", "查看师资力量"],
            IntentType.PRICE_INQUIRY: ["查看优惠活动", "了解分期方案", "对比课程价格"],
            IntentType.CHITCHAT: ["我想咨询留学", "你们有什么课程？", "最近有什么活动？"],
            IntentType.REGISTRATION: ["确认报名信息", "了解活动详情", "添加顾问微信"],
        }
        return suggestions_map.get(intent, ["我想了解更多", "帮我预约咨询", "查看成功案例"])


class RegistrationService:
    """Handle activity registrations."""

    async def register(self, request: Any) -> Any:
        from src.common.schemas import RegistrationResponse
        # TODO: persist to DB
        return RegistrationResponse(
            registration_id=1,
            status="confirmed",
            message="报名成功！我们的顾问会在24小时内联系您。",
        )


# Service singletons
agent_service = CustomerAgentService()
registration_service = RegistrationService()
