import uuid
from pathlib import Path

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}


def validate_file_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {ext}")
    return ext


def safe_filename(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return f"{uuid.uuid4().hex}{ext}"
