import pytest

from app.services.retrieval_service import RetrievalService


class FakeEmbeddingClient:
    async def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class FakeChunkRepository:
    async def vector_search(
        self,
        query_vector,
        top_k,
        document_ids=None,
    ):
        return [
            {
                "document_id": "doc-1",
                "text": "Relevant result",
                "score": 0.9,
            },
            {
                "document_id": "doc-2",
                "text": "Weak result",
                "score": 0.5,
            },
        ]


@pytest.mark.anyio
async def test_search_rejects_invalid_document_id():
    service = RetrievalService(
        chunk_repository=FakeChunkRepository(),
        embedding_client=FakeEmbeddingClient(),
    )

    with pytest.raises(ValueError, match="Invalid document_id"):
        await service.search(
            question="What framework do we use?",
            document_ids=["123"],
        )


@pytest.mark.anyio
async def test_search_filters_results_by_score(monkeypatch):
    monkeypatch.setattr(
        "app.services.retrieval_service.settings.score_threshold",
        0.8,
    )

    service = RetrievalService(
        chunk_repository=FakeChunkRepository(),
        embedding_client=FakeEmbeddingClient(),
    )

    results = await service.search(
        question="What framework do we use?",
    )

    assert len(results) == 1
    assert results[0]["document_id"] == "doc-1"
    assert results[0]["score"] == 0.9