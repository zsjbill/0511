"""
M4: Life Knowledge — Overseas life knowledge base RAG.
"""
import logging
from typing import Any

from src.common.vector_store import vector_store

logger = logging.getLogger(__name__)


class LifeKnowledge:
    """Search overseas life knowledge base."""

    async def search(self, student_id: int, query: str) -> dict[str, Any]:
        """Search life knowledge base for relevant information."""
        if not query:
            return {"results": [], "message": "请输入查询内容"}

        try:
            results = await vector_store.search(query, top_k=5)
        except Exception:
            results = []

        return {
            "student_id": student_id,
            "query": query,
            "results": results,
        }
