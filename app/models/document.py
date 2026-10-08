from datetime import datetime, timezone

from bson import ObjectId


def create_document(
    filename: str,
    content_hash: str,
) -> dict:
    return {
        "_id": ObjectId(),
        "filename": filename,
        "content_hash": content_hash,
        "status": "processing",
        "chunks_count": 0,
        "created_at": datetime.now(timezone.utc),
    }