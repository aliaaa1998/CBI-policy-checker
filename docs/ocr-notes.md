# OCR Notes

- Primary: PaddleOCR (`lang=ar`)
- Fallback: Tesseract (`ara` language pack)
- Preprocessing: grayscale, denoise, adaptive threshold, deskew
- Low confidence pages are flagged when confidence < configured threshold.
