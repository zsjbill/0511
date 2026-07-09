"""
LLM API client — unified wrapper for OpenAI / 通义千问 / 智谱 etc.
"""
import json
import logging
from typing import Any, AsyncIterator, Optional

from config.settings import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified LLM client with provider abstraction."""

    def __init__(self) -> None:
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self._async_client = None

    async def initialize(self) -> None:
        """Set up the async client for the configured provider."""
        if self.provider == "openai":
            from openai import AsyncOpenAI
            self._async_client = AsyncOpenAI(
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL,
            )
        else:
            # Generic OpenAI-compatible endpoint (covers 通义千问, 智谱, etc.)
            from openai import AsyncOpenAI
            self._async_client = AsyncOpenAI(
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL or "https://api.openai.com/v1",
            )
        logger.info("LLM client initialized: provider=%s model=%s", self.provider, self.model)

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[dict[str, Any]] = None,
    ) -> str:
        """Send a chat completion request and return the text response."""
        if self._async_client is None:
            await self.initialize()

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or settings.LLM_TEMPERATURE,
            "max_tokens": max_tokens or settings.LLM_MAX_TOKENS,
        }
        if response_format:
            kwargs["response_format"] = response_format

        response = await self._async_client.chat.completions.create(**kwargs)  # type: ignore[union-attr]
        return response.choices[0].message.content or ""

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
    ) -> AsyncIterator[str]:
        """Stream a chat completion."""
        if self._async_client is None:
            await self.initialize()

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or settings.LLM_TEMPERATURE,
            "stream": True,
        }

        stream = await self._async_client.chat.completions.create(**kwargs)  # type: ignore[union-attr]
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

    async def chat_json(self, messages: list[dict[str, str]], **kwargs: Any) -> dict[str, Any]:
        """Chat and parse the response as JSON."""
        text = await self.chat(messages, response_format={"type": "json_object"}, **kwargs)
        return json.loads(text)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        if self._async_client is None:
            await self.initialize()

        response = await self._async_client.embeddings.create(  # type: ignore[union-attr]
            model=settings.EMBEDDING_MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]


# Singleton
llm_client = LLMClient()
