from app.services.chunking_service import chunk_pages, chunk_text


def test_chunk_text_returns_empty_list_for_empty_text():
    result = chunk_text("", page=1)

    assert result == []


def test_chunk_text_splits_text_into_chunks(monkeypatch):
    monkeypatch.setattr("app.services.chunking_service.settings.chunk_size", 10)
    monkeypatch.setattr("app.services.chunking_service.settings.chunk_overlap", 2)

    text = "abcdefghijklmnopqrstuvwxyz"

    result = chunk_text(text, page=1)

    assert len(result) == 4
    assert result[0]["text"] == "abcdefghij"
    assert result[0]["page"] == 1
    assert result[0]["chunk_index"] == 0


def test_chunk_text_preserves_overlap(monkeypatch):
    monkeypatch.setattr("app.services.chunking_service.settings.chunk_size", 10)
    monkeypatch.setattr("app.services.chunking_service.settings.chunk_overlap", 2)

    text = "abcdefghijklmnopqrstuvwxyz"

    result = chunk_text(text, page=1)

    assert result[1]["text"].startswith(
        result[0]["text"][-2:]
    )


def test_chunk_pages_keeps_global_chunk_index(monkeypatch):
    monkeypatch.setattr("app.services.chunking_service.settings.chunk_size", 10)
    monkeypatch.setattr("app.services.chunking_service.settings.chunk_overlap", 2)

    pages = [
        {"page": 1, "text": "abcdefghijk"},
        {"page": 2, "text": "lmnopqrstuv"},
    ]

    result = chunk_pages(pages)

    assert [chunk["chunk_index"] for chunk in result] == list(
        range(len(result))
    )

    assert result[0]["page"] == 1
    assert result[-1]["page"] == 2