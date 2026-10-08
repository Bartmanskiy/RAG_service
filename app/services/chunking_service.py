from app.config import settings


def chunk_text(
    text: str,
    page: int | None,
) -> list[dict]:
    text = text.strip()

    if not text:
        return []

    chunks = []

    start = 0
    chunk_index = 0

    while start < len(text):
        end = start + settings.chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(
                {
                    "text": chunk,
                    "page": page,
                    "chunk_index": chunk_index,
                }
            )

            chunk_index += 1

        start += settings.chunk_size - settings.chunk_overlap

    return chunks


def chunk_pages(
    pages: list[dict],
) -> list[dict]:
    chunks = []

    chunk_index = 0

    for page_data in pages:
        page_chunks = chunk_text(
            text=page_data["text"],
            page=page_data["page"],
        )

        for chunk in page_chunks:
            chunk["chunk_index"] = chunk_index
            chunks.append(chunk)
            chunk_index += 1

    return chunks
