import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.entities import ComplianceRun, IngestionRun, QueryRun
from app.repositories.documents import DocumentRepository
from app.schemas.compliance import ComplianceRequest, ComplianceResponse
from app.schemas.document import DocumentOut, IngestResponse
from app.schemas.index import IndexStats
from app.schemas.query import QueryRequest, QueryResponse
from app.services.compliance.openai_responder import ResponseService
from app.services.embeddings.openai_embedder import EmbeddingService
from app.services.pipeline import IngestionService
from app.services.retrieval.faiss_store import faiss_store

router = APIRouter()

def _read_prompt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _qa_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "answer": {"type": "string"},
            "citations": {"type": "array", "items": {"type": "object", "properties": {"document": {"type": "string"}, "page": {"type": "integer"}, "section": {"type": ["string", "null"]}, "chunk_id": {"type": ["string", "null"]}}, "required": ["document", "page", "section", "chunk_id"], "additionalProperties": False}},
            "support_level": {"type": "string", "enum": ["low", "medium", "high"]},
            "notes": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["answer", "citations", "support_level", "notes"],
        "additionalProperties": False,
    }


def _compliance_schema() -> dict:
    citation = {"type": "object", "properties": {"document": {"type": "string"}, "page": {"type": "integer"}, "section": {"type": ["string", "null"]}}, "required": ["document", "page", "section"], "additionalProperties": False}
    return {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["compliant", "non_compliant", "unclear"]},
            "summary": {"type": "string"},
            "violations": {"type": "array", "items": {"type": "object", "properties": {"issue": {"type": "string"}, "severity": {"type": "string", "enum": ["low", "medium", "high"]}, "explanation": {"type": "string"}, "citation": citation}, "required": ["issue", "severity", "explanation", "citation"], "additionalProperties": False}},
            "relevant_clauses": {"type": "array", "items": {"type": "object", "properties": {"clause_text": {"type": "string"}, "citation": citation}, "required": ["clause_text", "citation"], "additionalProperties": False}},
            "required_actions": {"type": "array", "items": {"type": "string"}},
            "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
            "needs_human_review": {"type": "boolean"},
        },
        "required": ["verdict", "summary", "violations", "relevant_clauses", "required_actions", "confidence", "needs_human_review"],
        "additionalProperties": False,
    }


@router.get("/healthz")
def healthz():
    return {"status": "ok"}


@router.get("/readyz")
def readyz(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ready"}


@router.post("/documents/ingest", response_model=IngestResponse)
def ingest_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    request_id = uuid.uuid4().hex
    if file.size and file.size > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")
    run = IngestionRun(status="started", request_id=request_id, details={"filename": file.filename})
    db.add(run)
    db.flush()
    payload = IngestionService().ingest(db, file, request_id)
    run.status = "completed"
    run.details = {"chunks_indexed": payload["chunks_indexed"]}
    db.commit()
    doc = payload["document"]
    return IngestResponse(
        run_id=run.id,
        request_id=request_id,
        document=DocumentOut.model_validate(doc.__dict__),
        chunks_indexed=payload["chunks_indexed"],
        low_confidence_pages=payload["low_confidence_pages"],
    )


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    docs = DocumentRepository(db).list_documents()
    return [DocumentOut.model_validate(d.__dict__) for d in docs]


@router.get("/documents/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = DocumentRepository(db).get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentOut.model_validate(doc.__dict__)


@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest, db: Session = Depends(get_db)):
    request_id = uuid.uuid4().hex
    top_k = req.top_k or settings.retrieval_top_k
    embed = EmbeddingService().embed([req.question])[0]
    hits = faiss_store.search(embed, top_k)
    payload = {"question": req.question, "response_language": req.response_language, "evidence": hits}
    result = ResponseService().ask(_read_prompt("app/prompts/query.md"), payload, _qa_schema())
    db.add(QueryRun(request_id=request_id, question=req.question, model=settings.openai_response_model, response=result))
    db.commit()
    return QueryResponse(**result, request_id=request_id)


@router.post("/compliance/check", response_model=ComplianceResponse)
def compliance_check(req: ComplianceRequest, db: Session = Depends(get_db)):
    request_id = uuid.uuid4().hex
    top_k = req.top_k or settings.retrieval_top_k
    embed = EmbeddingService().embed([req.scenario])[0]
    hits = faiss_store.search(embed, top_k)
    payload = {"scenario": req.scenario, "response_language": req.response_language, "evidence": hits}
    result = ResponseService().ask(_read_prompt("app/prompts/compliance_check.md"), payload, _compliance_schema())
    db.add(ComplianceRun(request_id=request_id, scenario=req.scenario, model=settings.openai_response_model, response=result))
    db.commit()
    return ComplianceResponse(**result, request_id=request_id)


@router.get("/index/stats", response_model=IndexStats)
def index_stats(db: Session = Depends(get_db)):
    repo = DocumentRepository(db)
    stats = faiss_store.stats()
    return IndexStats(documents=len(repo.list_documents()), chunks=repo.chunks_count(), vectors=stats["vectors"], last_rebuild_at=None)


@router.post("/index/rebuild")
def rebuild_index():
    faiss_store.load()
    return {"status": "reloaded", "vectors": faiss_store.stats()["vectors"]}


@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    return {
        "ingestion": [r.id for r in db.scalars(select(IngestionRun).order_by(IngestionRun.id.desc()).limit(20))],
        "query": [r.id for r in db.scalars(select(QueryRun).order_by(QueryRun.id.desc()).limit(20))],
        "compliance": [r.id for r in db.scalars(select(ComplianceRun).order_by(ComplianceRun.id.desc()).limit(20))],
    }


@router.get("/runs/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.get(IngestionRun, run_id) or db.get(QueryRun, run_id) or db.get(ComplianceRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"id": run.id, "type": run.__class__.__name__, "created_at": run.created_at}
