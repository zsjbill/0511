"""
Vector database client abstraction (Chroma / FAISS / Pinecone).
"""
import logging
from typing import Optional

from config.settings import settings

logger = logging.getLogger(__name__)


class VectorStoreClient:
    """Unified vector store interface."""

    def __init__(self) -> None:
        self.store_type = settings.VECTOR_STORE_TYPE
        self._client = None

    async def initialize(self) -> None:
        """Connect to the configured vector store."""
        if self.store_type == "chroma":
            self._init_chroma()
        elif self.store_type == "faiss":
            self._init_faiss()
        elif self.store_type == "pinecone":
            self._init_pinecone()
        else:
            raise ValueError(f"Unsupported vector store: {self.store_type}")
        logger.info("Vector store initialized: %s", self.store_type)

    def _init_chroma(self) -> None:
        try:
            import chromadb
            self._client = chromadb.PersistentClient(path=settings.VECTOR_STORE_PATH)
        except ImportError:
            logger.warning("chromadb not installed; vector features disabled")

    def _init_faiss(self) -> None:
        try:
            import faiss
            self._client = None  # FAISS is used in-process, no persistent client
        except ImportError:
            logger.warning("faiss not installed; vector features disabled")

    def _init_pinecone(self) -> None:
        try:
            import pinecone
            self._client = None  # Requires API key config
        except ImportError:
            logger.warning("pinecone not installed; vector features disabled")

    async def add_documents(self, texts: list[str], metadatas: Optional[list[dict]] = None,
                            ids: Optional[list[str]] = None) -> None:
        """Embed and store documents."""
        raise NotImplementedError

    async def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Semantic search."""
        raise NotImplementedError

    async def delete(self, ids: list[str]) -> None:
        """Delete documents by ID."""
        raise NotImplementedError


# Singleton
vector_store = VectorStoreClient()
