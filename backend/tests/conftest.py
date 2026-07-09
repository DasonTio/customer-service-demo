import uuid
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from src.database import get_db
from src.llm.dependencies import get_llm
from src.main import app
from src.rag.retriever import RetrievedChunk


class FakeLLM:
    """Stands in for OllamaClient: deterministic embeddings, canned stream."""

    def __init__(self, tokens: list[str] | None = None) -> None:
        self.tokens = tokens or ["Hello", " there"]
        self.embed_calls: list[list[str]] = []

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.embed_calls.append(texts)
        return [[0.1] * 768 for _ in texts]

    async def chat_stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        self.messages = messages
        for token in self.tokens:
            yield token


@pytest.fixture
def fake_llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture
def sample_chunk() -> RetrievedChunk:
    return RetrievedChunk(
        document_id=uuid.uuid4(),
        filename="faq.md",
        chunk_index=0,
        content="Refunds are available within 30 days of purchase.",
        distance=0.2,
    )


@pytest.fixture
async def client(fake_llm: FakeLLM) -> AsyncIterator[AsyncClient]:
    app.dependency_overrides[get_llm] = lambda: fake_llm
    app.dependency_overrides[get_db] = lambda: None
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
