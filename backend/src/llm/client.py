import json
from collections.abc import AsyncIterator

import httpx

from src.llm.config import llm_settings
from src.llm.exceptions import LLMUnavailable


class OllamaClient:
    """Thin async client for the Ollama HTTP API (embeddings + streaming chat)."""

    def __init__(self, base_url: str | None = None) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url or llm_settings.OLLAMA_BASE_URL,
            timeout=llm_settings.REQUEST_TIMEOUT_SECONDS,
        )

    async def close(self) -> None:
        await self._http.aclose()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            response = await self._http.post(
                "/api/embed",
                json={"model": llm_settings.EMBED_MODEL, "input": texts},
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMUnavailable() from exc
        return response.json()["embeddings"]

    async def chat_stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        try:
            async with self._http.stream(
                "POST",
                "/api/chat",
                json={"model": llm_settings.CHAT_MODEL, "messages": messages, "stream": True},
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    payload = json.loads(line)
                    token = payload.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if payload.get("done"):
                        return
        except httpx.HTTPError as exc:
            raise LLMUnavailable() from exc
