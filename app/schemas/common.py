from pydantic import BaseModel


class Citation(BaseModel):
    document: str
    page: int
    section: str | None = None
    chunk_id: str | None = None
