import re
from dataclasses import dataclass


@dataclass
class Chunk:
    chunk_index: int
    text: str
    section_title: str | None


SECTION_RE = re.compile(r"^(المادة|الفصل|القسم)\s+.+", re.MULTILINE)


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[Chunk]:
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, idx = [], 0
    buffer = ""
    section = None
    for p in paragraphs:
        if SECTION_RE.match(p):
            section = p
        if len(buffer) + len(p) + 1 <= chunk_size:
            buffer += ("\n" if buffer else "") + p
            continue
        if buffer:
            chunks.append(Chunk(chunk_index=idx, text=buffer, section_title=section))
            idx += 1
        tail = buffer[-overlap:] if overlap > 0 else ""
        buffer = (tail + "\n" + p).strip()
    if buffer:
        chunks.append(Chunk(chunk_index=idx, text=buffer, section_title=section))
    return chunks
