# Architecture Notes

The service uses OCR-first ingestion to transform scanned Arabic policies into normalized chunks indexed in FAISS. PostgreSQL stores metadata and run audits. OpenAI embeddings power semantic search and OpenAI Responses API returns schema-validated answers and compliance verdicts.
