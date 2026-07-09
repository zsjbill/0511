"""
M5: Unit tests for Report Module.
"""
import pytest
from src.module_m5_report.data_aggregator import DataAggregator


class TestDataAggregator:
    def setup_method(self) -> None:
        self.aggregator = DataAggregator()

    @pytest.mark.asyncio
    async def test_collect_daily(self) -> None:
        data = await self.aggregator.collect("daily")
        assert "new_inquiries" in data
        assert "registrations" in data

    @pytest.mark.asyncio
    async def test_collect_weekly(self) -> None:
        data = await self.aggregator.collect("weekly")
        assert "total_inquiries" in data
