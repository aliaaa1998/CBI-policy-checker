import logging

from app.core.config import settings
from app.core.security import safe_filename, validate_file_extension
from app.repositories.documents import DocumentRepository
from app.services.embeddings.openai_embedder import EmbeddingService
from app.services.normalization.arabic import normalize_arabic
from app.services.ocr.pipeline import collect_pages, run_ocr_on_image
from app.services.preprocessing.image import preprocess_image
from app.services.retrieval.chunking import chunk_text
from app.services.retrieval.faiss_store import faiss_store

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self) -> None:
        self.embedder = EmbeddingService()

    def ingest(self, db, uploaded_file, request_id: str) -> dict:
        validate_file_extension(uploaded_file.filename)
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        raw_path = settings.upload_dir / safe_filename(uploaded_file.filename)
        raw_path.write_bytes(uploaded_file.file.read())
        page_dir = settings.upload_dir / raw_path.stem
        page_dir.mkdir(parents=True, exist_ok=True)

        images = collect_pages(raw_path, page_dir)
        repo = DocumentRepository(db)
        doc = repo.create_document(title=uploaded_file.filename, source_filename=raw_path.name, page_count=len(images))
        low_conf = []
        chunk_metas, chunk_texts = [], []

        for i, image in enumerate(images, start=1):
            preprocessed = page_dir / f"pre_{i}.png"
            preprocess_image(image, preprocessed)
            text, engine, conf = run_ocr_on_image(preprocessed)
            normalized = normalize_arabic(text)
            repo.add_page(
                document_id=doc.id,
                page_number=i,
                ocr_engine=engine,
                ocr_confidence=conf,
                original_text=text,
                normalized_text=normalized,
            )
            if conf is None or conf < settings.low_confidence_threshold:
                low_conf.append(i)
            for ch in chunk_text(normalized, settings.chunk_size, settings.chunk_overlap):
                c = repo.add_chunk(
                    document_id=doc.id,
                    page_number=i,
                    chunk_index=ch.chunk_index,
                    section_title=ch.section_title,
                    original_text=text,
                    normalized_text=ch.text,
                    ocr_confidence=conf,
                )
                meta = {
                    "chunk_id": str(c.id),
                    "document_id": doc.id,
                    "document": doc.title,
                    "source_filename": doc.source_filename,
                    "page": i,
                    "section": ch.section_title,
                    "text": ch.text,
                    "ocr_confidence": conf,
                }
                chunk_metas.append(meta)
                chunk_texts.append(ch.text)

        vectors = self.embedder.embed(chunk_texts) if chunk_texts else []
        if vectors:
            faiss_store.add(vectors, chunk_metas)
        db.commit()
        logger.info("ingestion_completed", extra={"request_id": request_id, "run_id": None})
        return {
            "document": doc,
            "chunks_indexed": len(chunk_texts),
            "low_confidence_pages": low_conf,
        }
