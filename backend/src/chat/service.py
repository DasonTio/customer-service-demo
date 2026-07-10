import json
from collections.abc import AsyncIterator

from src.chat.constants import (
    GUARDRAIL_REMINDER,
    MAX_HISTORY_MESSAGES,
    NO_CONTEXT_PLACEHOLDER,
    SYSTEM_PROMPT_TEMPLATE,
)
from src.chat.schemas import ChatRequest
from src.llm.client import GeminiClient
from src.llm.exceptions import LLMUnavailable
from src.rag.retriever import RetrievedChunk


def format_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def build_messages(payload: ChatRequest, chunks: list[RetrievedChunk]) -> list[dict[str, str]]:
    if chunks:
        context = "\n\n---\n\n".join(f"[Source: {c.filename}]\n{c.content}" for c in chunks)
    else:
        context = NO_CONTEXT_PLACEHOLDER

    messages = [{"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(context=context)}]
    for message in payload.history[-MAX_HISTORY_MESSAGES:]:
        messages.append({"role": message.role.value, "content": message.content})
    messages.append({"role": "user", "content": payload.message})
    messages.append({"role": "system", "content": GUARDRAIL_REMINDER})
    return messages


async def stream_answer(
    llm: GeminiClient,
    payload: ChatRequest,
    chunks: list[RetrievedChunk],
) -> AsyncIterator[str]:
    """Yield SSE frames: sources first, then tokens, then done (or error)."""
    yield format_sse(
        "sources",
        {
            "sources": [
                {
                    "document_id": str(c.document_id),
                    "filename": c.filename,
                    "chunk_index": c.chunk_index,
                }
                for c in chunks
            ]
        },
    )
    try:
        async for token in llm.chat_stream(build_messages(payload, chunks)):
            yield format_sse("token", {"text": token})
    except LLMUnavailable:
        yield format_sse("error", {"detail": "The language model service is unavailable."})
        return
    yield format_sse("done", {})
