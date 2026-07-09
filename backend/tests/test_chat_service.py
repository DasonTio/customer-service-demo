import json

from src.chat import service
from src.chat.constants import NO_CONTEXT_PLACEHOLDER
from src.chat.schemas import ChatMessage, ChatRequest, Role
from tests.conftest import FakeLLM


def parse_sse(raw: str) -> list[tuple[str, dict]]:
    events = []
    for frame in raw.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in frame.split("\n"))
        events.append((lines["event"], json.loads(lines["data"])))
    return events


def test_build_messages_includes_context_and_history(sample_chunk):
    payload = ChatRequest(
        message="Can I get a refund?",
        history=[
            ChatMessage(role=Role.USER, content="Hi"),
            ChatMessage(role=Role.ASSISTANT, content="Hello! How can I help?"),
        ],
    )
    messages = service.build_messages(payload, [sample_chunk])

    assert messages[0]["role"] == "system"
    assert "Refunds are available within 30 days" in messages[0]["content"]
    assert "faq.md" in messages[0]["content"]
    assert [m["role"] for m in messages[1:]] == ["user", "assistant", "user"]
    assert messages[-1]["content"] == "Can I get a refund?"


def test_build_messages_without_context_uses_placeholder():
    payload = ChatRequest(message="What's your refund policy?")
    messages = service.build_messages(payload, [])
    assert NO_CONTEXT_PLACEHOLDER in messages[0]["content"]


def test_build_messages_caps_history():
    history = [ChatMessage(role=Role.USER, content=f"message {i}") for i in range(30)]
    payload = ChatRequest(message="latest", history=history)
    messages = service.build_messages(payload, [])
    # system + capped history + current message
    assert len(messages) == 1 + 10 + 1
    assert messages[1]["content"] == "message 20"


async def test_stream_answer_frames(sample_chunk):
    llm = FakeLLM(tokens=["Ref", "unds", " in 30 days."])
    payload = ChatRequest(message="Refund policy?")

    raw = "".join([frame async for frame in service.stream_answer(llm, payload, [sample_chunk])])
    events = parse_sse(raw)

    assert events[0][0] == "sources"
    assert events[0][1]["sources"][0]["filename"] == "faq.md"
    tokens = [data["text"] for name, data in events if name == "token"]
    assert "".join(tokens) == "Refunds in 30 days."
    assert events[-1][0] == "done"
