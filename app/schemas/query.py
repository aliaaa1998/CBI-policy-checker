from pydantic import BaseModel, Field

from app.schemas.common import Citation


class QueryRequest(BaseModel):
    question: str = Field(min_length=3)
    response_language: str = "ar"
    top_k: int | None = None


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    support_level: str
    notes: list[str]
    request_id: str
