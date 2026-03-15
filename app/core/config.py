from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CBI Policy Compliance RAG"
    app_env: str = "dev"
    api_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/cbi"
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_response_model: str = "gpt-4.1-mini"

    artifacts_dir: Path = Path("artifacts")
    upload_dir: Path = Path("artifacts/uploads")
    index_dir: Path = Path("artifacts/indexes")
    faiss_index_file: str = "policy.index"
    faiss_meta_file: str = "policy_meta.json"

    max_upload_size_mb: int = 20
    retrieval_top_k: int = 6
    chunk_size: int = 900
    chunk_overlap: int = 140
    low_confidence_threshold: float = 0.65
    default_response_language: str = "ar"


settings = Settings()
