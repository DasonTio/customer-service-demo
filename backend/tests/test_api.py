import io

from httpx import AsyncClient

from src.rag import retriever


async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_upload_rejects_unsupported_file_type(client: AsyncClient):
    resp = await client.post(
        "/documents",
        files={"file": ("photo.png", io.BytesIO(b"\x89PNG"), "image/png")},
    )
    assert resp.status_code == 415


async def test_chat_streams_sse(client: AsyncClient, sample_chunk, monkeypatch):
    async def fake_retrieve(db, llm, query, **kwargs):
        return [sample_chunk]

    monkeypatch.setattr(retriever, "retrieve", fake_retrieve)

    resp = await client.post("/chat", json={"message": "Refund policy?"})
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")
    body = resp.text
    assert "event: sources" in body
    assert "event: token" in body
    assert body.strip().endswith("data: {}")


async def test_chat_validates_empty_message(client: AsyncClient):
    resp = await client.post("/chat", json={"message": ""})
    assert resp.status_code == 422
