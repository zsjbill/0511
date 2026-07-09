"""
M3: Unit tests for Enterprise Assistant.
"""
import pytest
from src.module_m3_enterprise_assistant.nl2sql_engine import NL2SQLEngine


class TestNL2SQLEngine:
    def setup_method(self) -> None:
        self.engine = NL2SQLEngine()

    @pytest.mark.asyncio
    async def test_generate_sql_returns_string(self) -> None:
        sql = await self.engine._generate_sql("查询所有员工")
        assert isinstance(sql, str)
        assert len(sql) > 0
