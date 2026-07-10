import json
from collections.abc import AsyncIterator

import httpx

from src.llm.config import llm_settings
from src.llm.exceptions import LLMUnavailable

_ROLE_MAP = {"user": "user", "assistant": "model"}


def _to_gemini_payload(messages: list[dict[str, str]]) -> tuple[str | None, list[dict]]:
    """Translate a flat OpenAI/Ollama-style message list into Gemini's shape.

    System messages before the last user turn become ``systemInstruction``.
    A system message placed *after* the last user turn (used to anchor a
    guardrail reminder as close to generation as possible) is folded into
    that user turn as an extra part, since Gemini has no equivalent slot.
    """
    last_user_index = max(
        (i for i, m in enumerate(messages) if m["role"] == "user"), default=-1
    )

    system_parts: list[str] = []
    contents: list[dict] = []
    for i, message in enumerate(messages):
        role = message["role"]
        if role == "system":
            if i > last_user_index >= 0:
                contents[-1]["parts"].append({"text": message["content"]})
            else:
                system_parts.append(message["content"])
            continue
        contents.append({"role": _ROLE_MAP[role], "parts": [{"text": message["content"]}]})

    system_instruction = "\n\n".join(system_parts) if system_parts else None
    return system_instruction, contents


class GeminiClient:
    """Thin async client for the Gemini API (embeddings + streaming chat)."""

    def __init__(self, base_url: str | None = None) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url or llm_settings.GEMINI_BASE_URL,
            headers={"x-goog-api-key": llm_settings.GEMINI_API_KEY},
            timeout=llm_settings.REQUEST_TIMEOUT_SECONDS,
        )

    async def close(self) -> None:
        await self._http.aclose()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        model = f"models/{llm_settings.EMBED_MODEL}"
        try:
            response = await self._http.post(
                f"/v1beta/{model}:batchEmbedContents",
                json={
                    "requests": [
                        {
                            "model": model,
                            "content": {"parts": [{"text": text}]},
                            "output_dimensionality": llm_settings.EMBED_DIM,
                        }
                        for text in texts
                    ]
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMUnavailable() from exc
        return [item["values"] for item in response.json()["embeddings"]]

    async def chat_stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        system_instruction, contents = _to_gemini_payload(messages)
        body: dict = {"contents": contents}
        if system_instruction:
            body["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        try:
            async with self._http.stream(
                "POST",
                f"/v1beta/models/{llm_settings.CHAT_MODEL}:streamGenerateContent",
                params={"alt": "sse"},
                json=body,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    payload = json.loads(line[len("data: ") :])
                    for candidate in payload.get("candidates", []):
                        for part in candidate.get("content", {}).get("parts", []):
                            text = part.get("text", "")
                            if text:
                                yield text
        except httpx.HTTPError as exc:
            raise LLMUnavailable() from exc
