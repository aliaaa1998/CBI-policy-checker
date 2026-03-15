from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    title: str
    source_filename: str
    page_count: int
    created_at: datetime


class IngestResponse(BaseModel):
    run_id: int
    request_id: str
    document: DocumentOut
    chunks_indexed: int
    low_confidence_pages: list[int]
