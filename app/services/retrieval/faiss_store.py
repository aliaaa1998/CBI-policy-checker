import json

import faiss
import numpy as np

from app.core.config import settings


class FaissStore:
    def __init__(self) -> None:
        self.index_path = settings.index_dir / settings.faiss_index_file
        self.meta_path = settings.index_dir / settings.faiss_meta_file
        self.index = None
        self.metadata: dict[str, dict] = {}
        settings.index_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> None:
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
        if self.meta_path.exists():
            self.metadata = json.loads(self.meta_path.read_text())

    def init_if_needed(self, dim: int) -> None:
        if self.index is None:
            self.index = faiss.IndexFlatIP(dim)

    def add(self, vectors: list[list[float]], metas: list[dict]) -> None:
        arr = np.array(vectors, dtype="float32")
        faiss.normalize_L2(arr)
        self.init_if_needed(arr.shape[1])
        start = self.index.ntotal
        self.index.add(arr)
        for i, m in enumerate(metas):
            self.metadata[str(start + i)] = m
        self.persist()

    def search(self, vector: list[float], k: int) -> list[dict]:
        if self.index is None or self.index.ntotal == 0:
            return []
        arr = np.array([vector], dtype="float32")
        faiss.normalize_L2(arr)
        _, ids = self.index.search(arr, k)
        hits = []
        for i in ids[0]:
            if i == -1:
                continue
            hits.append(self.metadata[str(i)])
        return hits

    def persist(self) -> None:
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
        self.meta_path.write_text(json.dumps(self.metadata, ensure_ascii=False, indent=2))

    def stats(self) -> dict:
        vectors = self.index.ntotal if self.index else 0
        return {"vectors": vectors, "metadata": len(self.metadata)}


faiss_store = FaissStore()
