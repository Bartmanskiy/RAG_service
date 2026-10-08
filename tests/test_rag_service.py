import pytest

from app.services.rag_service import RAGService


class EmptyRetrievalService:
    async def search(
        self,
        question,
        top_k=None,
        document_ids=None,
    ):
        return []


class FakeLLMClient:
    def __init__(self):
        self.generate_called = False
        self.last_prompt = None

    async def generate(self, prompt):
        self.generate_called = True
        self.last_prompt = prompt
        return "FastAPI"

    async def stream(self, prompt):
        yield "Fast"
        yield "API"


class FakeRetrievalService:
    async def search(
        self,
        question,
        top_k=None,
        document_ids=None,
    ):
        return [
            {
                "document_id": "doc-1",
                "text": "Our company uses FastAPI.",
                "document": {
                    "filename": "technologies.txt",
                },
                "page": 1,
                "score": 0.9,
            }
        ]


@pytest.mark.anyio
async def test_answer_does_not_call_llm_when_no_results():
    llm_client = FakeLLMClient()

    service = RAGService(
        retrieval_service=EmptyRetrievalService(),
        llm_client=llm_client,
    )

    result = await service.answer(
        question="What framework does our company use?"
    )

    assert result == {
        "answer": "У документах не знайдено інформації за цим запитом",
        "sources": [],
    }

    assert llm_client.generate_called is False


@pytest.mark.anyio
async def test_answer_calls_llm_with_retrieved_context():
    llm_client = FakeLLMClient()

    service = RAGService(
        retrieval_service=FakeRetrievalService(),
        llm_client=llm_client,
    )

    result = await service.answer(
        question="What framework does our company use?"
    )

    assert result["answer"] == "FastAPI"
    assert len(result["sources"]) == 1

    assert result["sources"][0]["document_id"] == "doc-1"
    assert result["sources"][0]["filename"] == "technologies.txt"
    assert result["sources"][0]["page"] == 1
    assert result["sources"][0]["score"] == 0.9
    assert result["sources"][0]["snippet"] == "Our company uses FastAPI."

    assert llm_client.generate_called is True
    assert "Our company uses FastAPI." in llm_client.last_prompt
    assert "What framework does our company use?" in llm_client.last_prompt


@pytest.mark.anyio
async def test_stream_answer_returns_sources_tokens_and_done():
    llm_client = FakeLLMClient()

    service = RAGService(
        retrieval_service=FakeRetrievalService(),
        llm_client=llm_client,
    )

    events = []

    async for event in service.stream_answer(
        question="What framework does our company use?"
    ):
        events.append(event)

    assert events[0].startswith("event: sources")
    assert any('"token": "Fast"' in event for event in events)
    assert any('"token": "API"' in event for event in events)
    assert events[-1] == "event: done\ndata: {}\n\n"


@pytest.mark.anyio
async def test_stream_answer_returns_empty_result_without_calling_llm():
    llm_client = FakeLLMClient()

    service = RAGService(
        retrieval_service=EmptyRetrievalService(),
        llm_client=llm_client,
    )

    events = []

    async for event in service.stream_answer(
        question="What framework does our company use?"
    ):
        events.append(event)

    assert events[0] == "event: sources\ndata: []\n\n"

    assert "У документах не знайдено інформації" in events[1]

    assert llm_client.generate_called is False