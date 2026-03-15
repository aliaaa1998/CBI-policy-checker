from pathlib import Path
from typing import Any

import pytesseract
from paddleocr import PaddleOCR

_paddle = None


def get_paddle() -> PaddleOCR:
    global _paddle
    if _paddle is None:
        _paddle = PaddleOCR(use_angle_cls=True, lang="ar", show_log=False)
    return _paddle


def run_paddle(image_path: Path) -> tuple[str, float | None]:
    result: list[Any] = get_paddle().ocr(str(image_path), cls=True)
    lines, confs = [], []
    for group in result:
        if not group:
            continue
        for item in group:
            lines.append(item[1][0])
            confs.append(float(item[1][1]))
    avg = sum(confs) / len(confs) if confs else None
    return "\n".join(lines).strip(), avg


def run_tesseract(image_path: Path) -> tuple[str, float | None]:
    data = pytesseract.image_to_data(str(image_path), lang="ara", output_type=pytesseract.Output.DICT)
    text = " ".join([t for t in data["text"] if t.strip()])
    confs = [float(c) for c in data["conf"] if c not in {"-1", -1}]
    avg = (sum(confs) / len(confs)) / 100 if confs else None
    return text.strip(), avg
