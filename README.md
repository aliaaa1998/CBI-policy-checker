# cbi-policy-compliance-rag

Arabic-first OCR + RAG compliance checker for Central Bank of Iraq (CBI)-style policy operations.

## Why this project matters
Organizations often receive policy updates as scanned PDFs and printed circulars. This repository demonstrates a production-minded backend service that digitizes Arabic policy artifacts and provides grounded policy Q&A and structured compliance verdicts with citations.

## Enterprise compliance use case
- Ingest scanned policy PDFs/images.
- OCR Arabic pages with confidence tracking.
- Normalize Arabic text for better retrieval.
- Retrieve policy evidence from FAISS.
- Produce OpenAI-backed structured outputs for audit-friendly compliance checks.

## Architecture overview
```mermaid
flowchart LR
  A[Scanned PDF/Image] --> B[Preprocessing]
  B --> C[Arabic OCR PaddleOCR]
  C -->|fallback| D[Tesseract ara]
  C --> E[Normalization + Chunking]
  D --> E
  E --> F[OpenAI Embeddings]
  F --> G[FAISS Index]
  E --> H[(PostgreSQL Metadata/Audit)]
  I[Query/Scenario] --> J[Retrieve Top-K]
  G --> J
  J --> K[OpenAI Responses API]
  H --> K
  K --> L[Structured JSON + Citations]
```

## Repository structure
```text
app/                FastAPI app, services, schemas, models
alembic/            DB migrations
examples/           Synthetic Arabic policy docs/scenarios/questions
tests/              Unit + integration tests
docs/               Architecture and OCR notes
artifacts/          OCR debug, indexes, reports
```

## Prerequisites
- Python 3.12
- Docker + Docker Compose
- OpenAI API key

## Environment variables
| Variable | Description | Default |
|---|---|---|
| OPENAI_API_KEY | OpenAI credential | (required for LLM/embeddings) |
| OPENAI_EMBEDDING_MODEL | embedding model | text-embedding-3-small |
| OPENAI_RESPONSE_MODEL | response model | gpt-4.1-mini |
| DATABASE_URL | SQLAlchemy DB URL | postgresql+psycopg://postgres:postgres@localhost:5432/cbi |
| RETRIEVAL_TOP_K | retrieval chunk count | 6 |
| CHUNK_SIZE | chunk size (chars) | 900 |
| CHUNK_OVERLAP | chunk overlap (chars) | 140 |

## Docker quickstart
```bash
cp .env.example .env
docker compose up --build
```

## Ingest scanned policy documents
```bash
curl -X POST http://localhost:8000/api/v1/documents/ingest \
  -F "file=@examples/policies/scanned/policy_kyc_1.pdf"
```

## Run a query
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"ما هي متطلبات التحقق من هوية العميل حسب السياسة؟","response_language":"ar"}'
```

## Run a compliance check
```bash
curl -X POST http://localhost:8000/api/v1/compliance/check \
  -H 'Content-Type: application/json' \
  -d '{"scenario":"فرع يريد فتح حساب باستخدام هوية ممسوحة فقط دون إثبات عنوان.","response_language":"ar"}'
```

## Example Q&A JSON response
```json
{
  "answer": "تشترط السياسة وثيقة هوية سارية وإثبات عنوان حديث.",
  "citations": [{"document":"policy_kyc_1.pdf","page":1,"section":"المادة 1","chunk_id":"14"}],
  "support_level": "high",
  "notes": ["لا توجد أدلة متعارضة"]
}
```

## Example compliance JSON response
```json
{
  "verdict": "non_compliant",
  "summary": "السيناريو غير متوافق لعدم تقديم إثبات العنوان.",
  "violations": [{"issue":"نقص وثائق إلزامية","severity":"high","explanation":"السياسة تتطلب إثبات عنوان.","citation":{"document":"policy_kyc_1.pdf","page":1,"section":"المادة 2"}}],
  "relevant_clauses": [{"clause_text":"يجب الحصول على إثبات عنوان حديث","citation":{"document":"policy_kyc_1.pdf","page":1,"section":"المادة 2"}}],
  "required_actions": ["استكمال إثبات العنوان قبل فتح الحساب"],
  "confidence": "high",
  "needs_human_review": false
}
```

## OCR engines and fallback
- Primary engine: PaddleOCR Arabic model.
- Fallback: Tesseract (`ara`) when PaddleOCR fails or yields empty text.
- Confidence is persisted per page; low-confidence pages are returned for manual review.

## FAISS indexing
- Embedding vectors are stored in local FAISS index files under `artifacts/indexes/`.
- Vector ID to metadata mapping is persisted in JSON.
- Supports startup load and incremental adds.

## Citation strategy
Each retrieved chunk carries document/page/section/chunk_id metadata, and the model is instructed to return only grounded citations from retrieved evidence.

## Arabic normalization choices
- Remove diacritics and tatweel.
- Normalize alef forms to `ا` and `ى` to `ي`.
- Normalize Arabic digits to Western digits.
- Keep original OCR text for evidence; normalized text for retrieval.

## Sample Arabic questions
See `examples/questions/questions_ar.txt`.

## Sample Arabic scenarios
See `examples/scenarios/scenarios_ar.txt`.

## Testing
```bash
make test
```

## Linting
```bash
make lint
```

## Troubleshooting
- OCR returns empty text: verify Tesseract Arabic language pack installed.
- DB issues: ensure postgres container is healthy.
- OpenAI errors: verify `OPENAI_API_KEY` and model availability.

## Design decisions and trade-offs
- FAISS used for speed and simple local persistence.
- PostgreSQL reserved for metadata/audit instead of vector storage.
- Responses API with JSON schema enforces machine-readable outputs.

## Limitations
- OCR quality depends on scan quality.
- Section header detection is regex-based and may miss complex layouts.
- Right-to-left rendering in synthetic examples is simplified.

## Roadmap
- Hybrid retrieval (BM25 + vector)
- Richer page layout OCR post-processing
- Human review workflow UI and approval chain

## Security / privacy / compliance disclaimer
This project is a decision-support system. It does not replace compliance officers, legal review, or official CBI policy interpretation.

## License
MIT (see `LICENSE`).
