from pydantic import BaseModel


class IndexStats(BaseModel):
    documents: int
    chunks: int
    vectors: int
    last_rebuild_at: str | None
