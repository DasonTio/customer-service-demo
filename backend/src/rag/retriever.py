import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.documents.models import Document, DocumentChunk
from src.llm.client import OllamaClient
from src.rag.constants import RETRIEVAL_MAX_DISTANCE, RETRIEVAL_TOP_K


@dataclass(frozen=True)
class RetrievedChunk:
    document_id: uuid.UUID
    filename: str
    chunk_index: int
    content: str
    distance: float


async def retrieve(
    db: AsyncSession,
    llm: OllamaClient,
    query: str,
    top_k: int = RETRIEVAL_TOP_K,
    max_distance: float = RETRIEVAL_MAX_DISTANCE,
) -> list[RetrievedChunk]:
    """Embed the query and return the closest chunks by cosine distance."""
    [query_embedding] = await llm.embed([query])

    distance = DocumentChunk.embedding.cosine_distance(query_embedding)
    result = await db.execute(
        select(DocumentChunk, Document.filename, distance.label("distance"))
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(distance < max_distance)
        .order_by(distance)
        .limit(top_k)
    )
    return [
        RetrievedChunk(
            document_id=chunk.document_id,
            filename=filename,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            distance=dist,
        )
        for chunk, filename, dist in result.all()
    ]
