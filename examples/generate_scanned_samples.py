from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
POLICIES = ROOT / "policies"
OUT = ROOT / "policies/scanned"
OUT.mkdir(parents=True, exist_ok=True)

for txt_file in POLICIES.glob("*.txt"):
    lines = txt_file.read_text(encoding="utf-8").splitlines()
    img = Image.new("RGB", (1800, 2400), "white")
    draw = ImageDraw.Draw(img)
    y = 120
    for line in lines:
        draw.text((120, y), line, fill="black")
        y += 80
    png_path = OUT / f"{txt_file.stem}.png"
    pdf_path = OUT / f"{txt_file.stem}.pdf"
    img.save(png_path)
    img.save(pdf_path, "PDF", resolution=100.0)

print(f"Generated scanned files in {OUT}")
