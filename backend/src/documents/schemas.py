from datetime import datetime

from pydantic import UUID4, BaseModel


class DocumentResponse(BaseModel):
    id: UUID4
    filename: str
    content_type: str
    created_at: datetime
    chunk_count: int
