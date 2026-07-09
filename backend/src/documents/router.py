from fastapi import APIRouter, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from src.database import DbSession
from src.documents import service
from src.documents.dependencies import ValidDocument
from src.documents.exceptions import UnsupportedFileType
from src.documents.schemas import DocumentResponse
from src.llm.dependencies import LLMClient

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a knowledge document",
    description="Extracts text, chunks it, embeds each chunk, and stores it for retrieval.",
)
async def upload_document(file: UploadFile, db: DbSession, llm: LLMClient):
    filename = file.filename or "untitled"
    if not service.is_supported(filename, file.content_type):
        raise UnsupportedFileType()

    data = await file.read()
    text = await run_in_threadpool(service.extract_text, filename, data)
    document = await service.ingest_document(
        db, llm, filename, file.content_type or "text/plain", text
    )
    chunk_count = await service.count_chunks(db, document.id)
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        content_type=document.content_type,
        created_at=document.created_at,
        chunk_count=chunk_count,
    )


@router.get("", response_model=list[DocumentResponse], summary="List ingested documents")
async def get_documents(db: DbSession):
    documents = await service.list_documents(db)
    return [
        DocumentResponse(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            created_at=document.created_at,
            chunk_count=count,
        )
        for document, count in documents
    ]


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document and its chunks",
)
async def delete_document(document: ValidDocument, db: DbSession) -> None:
    await service.delete_document(db, document)
