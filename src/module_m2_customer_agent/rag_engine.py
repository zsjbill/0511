"""
M2: RAG Engine — Retrieval-Augmented Generation.
"""
import logging
from typing import Any

from src.common.vector_store import vector_store

logger = logging.getLogger(__name__)


class RAGEngine:
    """Retrieve relevant documents and augment the LLM context."""

    def __init__(self) -> None:
        self.top_k = 5

    async def search(self, query: str) -> list[dict[str, Any]]:
        """Search the vector store for relevant context."""
        try:
            results = await vector_store.search(query, top_k=self.top_k)
            return results
        except NotImplementedError:
            logger.warning("Vector search not yet implemented; returning empty context")
            return []
        except Exception:
            logger.exception("RAG search failed")
            return []
