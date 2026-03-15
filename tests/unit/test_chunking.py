from app.services.retrieval.chunking import chunk_text


def test_chunking_overlap():
    txt = "\n".join(["فقرة " + str(i) for i in range(30)])
    chunks = chunk_text(txt, chunk_size=80, overlap=10)
    assert len(chunks) > 2
    assert chunks[0].chunk_index == 0
