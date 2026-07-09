import io
import uuid
from pathlib import Path

from pypdf import PdfReader
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.documents.constants import SUPPORTED_CONTENT_TYPES, SUPPORTED_EXTENSIONS
from src.documents.exceptions import EmptyDocument
from src.documents.models import Document, DocumentChunk
from src.llm.client import OllamaClient
from src.rag.chunker import chunk_text


def is_supported(filename: str, content_type: str | None) -> bool:
    if content_type in SUPPORTED_CONTENT_TYPES:
        return True
    return Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS


def extract_text(filename: str, data: bytes) -> str:
    """Sync and CPU-bound — call via run_in_threadpool from async routes."""
    if Path(filename).suffix.lower() == ".pdf":
        reader = PdfReader(io.BytesIO(data))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    return data.decode("utf-8", errors="replace")


async def ingest_document(
    db: AsyncSession,
    llm: OllamaClient,
    filename: str,
    content_type: str,
    text: str,
) -> Document:
    chunks = chunk_text(text)
    if not chunks or not any(c.strip() for c in chunks):
        raise EmptyDocument()

    embeddings = await llm.embed(chunks)

    document = Document(id=uuid.uuid4(), filename=filename, content_type=content_type)
    document.chunks = [
        DocumentChunk(chunk_index=i, content=content, embedding=embedding)
        for i, (content, embedding) in enumerate(zip(chunks, embeddings, strict=True))
    ]
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def list_documents(db: AsyncSession) -> list[tuple[Document, int]]:
    result = await db.execute(
        select(Document, func.count(DocumentChunk.id))
        .outerjoin(DocumentChunk)
        .group_by(Document.id)
        .order_by(Document.created_at.desc())
    )
    return [(document, count) for document, count in result.all()]


async def get_by_id(db: AsyncSession, document_id: uuid.UUID) -> Document | None:
    return await db.get(Document, document_id)


async def count_chunks(db: AsyncSession, document_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == document_id)
    )
    return result.scalar_one()


async def delete_document(db: AsyncSession, document: Document) -> None:
    await db.delete(document)
    await db.commit()
