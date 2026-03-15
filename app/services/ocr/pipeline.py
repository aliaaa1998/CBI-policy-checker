from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import fitz
from PIL import Image
from app.services.ocr.engines import run_paddle, run_tesseract
from app.services.preprocessing.image import preprocess_image


@dataclass
class OCRPageResult:
    page_number: int
    original_text: str
    normalized_text: str
    ocr_engine: str
    confidence: float | None
    extracted_at: datetime
    image_path: str


def pdf_to_images(pdf_path: Path, out_dir: Path) -> list[Path]:
    doc = fitz.open(pdf_path)
    images = []
    for idx, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        p = out_dir / f"page_{idx}.png"
        pix.save(p)
        images.append(p)
    return images


def collect_pages(path: Path, out_dir: Path) -> list[Path]:
    if path.suffix.lower() == ".pdf":
        return pdf_to_images(path, out_dir)
    img = Image.open(path)
    dst = out_dir / "page_1.png"
    img.save(dst)
    return [dst]


def run_ocr_on_image(image_path: Path) -> tuple[str, str, float | None]:
    try:
        text, conf = run_paddle(image_path)
        if text:
            return text, "paddleocr", conf
    except Exception:
        pass
    text, conf = run_tesseract(image_path)
    return text, "tesseract", conf
