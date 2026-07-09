from typing import Annotated

from fastapi import Depends
from pydantic import UUID4

from src.database import DbSession
from src.documents import service
from src.documents.exceptions import DocumentNotFound
from src.documents.models import Document


async def valid_document_id(document_id: UUID4, db: DbSession) -> Document:
    document = await service.get_by_id(db, document_id)
    if not document:
        raise DocumentNotFound()
    return document


ValidDocument = Annotated[Document, Depends(valid_document_id)]
