"""
E2E Test: Employee → Enterprise Assistant
"""
import pytest


class TestEmployeeFlow:
    """End-to-end employee journey."""

    @pytest.mark.asyncio
    async def test_nl2sql_query(self) -> None:
        """Test: employee asks NL question → SQL is generated."""
        pass

    @pytest.mark.asyncio
    async def test_org_query(self) -> None:
        """Test: employee queries org structure."""
        pass

    @pytest.mark.asyncio
    async def test_command_execution(self) -> None:
        """Test: '同意张三请假' → command is parsed and executed."""
        pass
