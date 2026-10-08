from bson import ObjectId


def create_chunk(
    document_id: ObjectId,
    text: str,
    embedding: list[float],
    page: int | None,
    chunk_index: int,
) -> dict:
    return {
        "_id": ObjectId(),
        "document_id": document_id,
        "text": text,
        "embedding": embedding,
        "page": page,
        "chunk_index": chunk_index,
    }