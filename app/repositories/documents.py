from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.entities import ChunkMetadata, Document, Page


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_document(self, title: str, source_filename: str, page_count: int) -> Document:
        doc = Document(title=title, source_filename=source_filename, page_count=page_count)
        self.db.add(doc)
        self.db.flush()
        return doc

    def add_page(self, **kwargs) -> Page:
        page = Page(**kwargs)
        self.db.add(page)
        return page

    def add_chunk(self, **kwargs) -> ChunkMetadata:
        chunk = ChunkMetadata(**kwargs)
        self.db.add(chunk)
        return chunk

    def list_documents(self) -> list[Document]:
        return list(self.db.scalars(select(Document).order_by(Document.id.desc())))

    def get_document(self, document_id: int) -> Document | None:
        return self.db.get(Document, document_id)

    def chunks_count(self) -> int:
        return self.db.query(ChunkMetadata).count()
