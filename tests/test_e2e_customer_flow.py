"""
E2E Test: Visitor → Customer Service → Registration
"""
import pytest


class TestCustomerFlow:
    """End-to-end customer journey."""

    @pytest.mark.asyncio
    async def test_full_registration_flow(self) -> None:
        """Test: visitor chats → gets recommendation → registers for activity."""
        # TODO: implement with TestClient
        pass

    @pytest.mark.asyncio
    async def test_customer_judge_flow(self) -> None:
        """Test: customer submits info → gets scored and tagged."""
        pass

    @pytest.mark.asyncio
    async def test_chat_intent_routing(self) -> None:
        """Test: various messages route to correct intent handler."""
        pass
