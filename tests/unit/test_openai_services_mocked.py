from types import SimpleNamespace

from app.services.compliance.openai_responder import ResponseService
from app.services.embeddings.openai_embedder import EmbeddingService


class FakeEmbeddingsClient:
    def create(self, model, input):
        return SimpleNamespace(data=[SimpleNamespace(embedding=[0.1, 0.2]) for _ in input])


class FakeResponsesClient:
    def create(self, **kwargs):
        return SimpleNamespace(output_text='{"answer":"ok","citations":[],"support_level":"low","notes":[]}')


def test_embedding_service_mocked(monkeypatch):
    service = EmbeddingService.__new__(EmbeddingService)
    service.client = SimpleNamespace(embeddings=FakeEmbeddingsClient())
    vectors = service.embed(["نص"])
    assert vectors == [[0.1, 0.2]]


def test_response_service_mocked(monkeypatch):
    service = ResponseService.__new__(ResponseService)
    service.client = SimpleNamespace(responses=FakeResponsesClient())
    out = service.ask("instr", {"x": 1}, {"type": "object"})
    assert out["answer"] == "ok"
