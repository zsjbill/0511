"""
Knowledge Base Search Tests — 3 tests for KB search functionality.
"""
import pytest
from src.module_student.kb_service import search_kb


class TestKBSearch:
    """KB search service unit tests."""

    @pytest.mark.asyncio
    async def test_search_returns_results(self):
        results = await search_kb("留学", top_k=3)
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_empty_query(self):
        results = await search_kb("", top_k=3)
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_top_k_limit(self):
        results = await search_kb("澳洲", top_k=3)
        assert len(results) <= 3
