"""
M2: Unit tests for Customer Agent.
"""
import pytest
from src.module_m2_customer_agent.intent_router import IntentRouter


class TestIntentRouter:
    def setup_method(self) -> None:
        self.router = IntentRouter()

    @pytest.mark.asyncio
    async def test_classify_has_return_type(self) -> None:
        intent, confidence = await self.router.classify("你们有什么课程？")
        assert intent is not None
        assert 0 <= confidence <= 1
