from pathlib import Path
from PIL import Image
from app.services.ocr.pipeline import collect_pages


def test_collect_pages_image(tmp_path):
    p = tmp_path / "x.png"
    Image.new("RGB", (100, 50), color=(255, 255, 255)).save(p)
    out = collect_pages(p, tmp_path / "out")
    assert len(out) == 1
    assert Path(out[0]).exists()
