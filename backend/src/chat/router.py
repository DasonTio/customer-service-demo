from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.chat import service
from src.chat.schemas import ChatRequest
from src.database import DbSession
from src.llm.dependencies import LLMClient
from src.rag import retriever

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "",
    summary="Chat with the customer service agent",
    description=(
        "Retrieves relevant knowledge base chunks and streams the agent's "
        "answer as Server-Sent Events: `sources`, `token`*, then `done`."
    ),
)
async def chat(payload: ChatRequest, db: DbSession, llm: LLMClient) -> StreamingResponse:
    # Retrieval happens before streaming starts so failures return real HTTP errors.
    chunks = await retriever.retrieve(db, llm, payload.message)
    return StreamingResponse(
        service.stream_answer(llm, payload, chunks),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
