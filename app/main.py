from fastapi import FastAPI
from app.api.v1.routes import router
from app.core.config import settings
from app.core.logging import configure_logging
from app.services.retrieval.faiss_store import faiss_store

configure_logging()
faiss_store.load()

app = FastAPI(title=settings.app_name)
app.include_router(router, prefix=settings.api_prefix)

@app.get("/")
def root():
    return {"service": settings.app_name}
