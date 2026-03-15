from app.services.retrieval.faiss_store import FaissStore


def test_faiss_metadata_mapping(tmp_path, monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "index_dir", tmp_path)
    s = FaissStore()
    s.add([[0.1, 0.2, 0.3]], [{"chunk_id": "1", "document": "d", "page": 1, "section": None, "text": "abc"}])
    hits = s.search([0.1, 0.2, 0.3], 1)
    assert hits[0]["chunk_id"] == "1"
