from pymongo.asynchronous.database import AsyncDatabase

from app.database import DOCUMENTS_COLLECTION, CHUNKS_COLLECTION


async def init_indexes(db: AsyncDatabase) -> None:
    documents = db[DOCUMENTS_COLLECTION]
    chunks = db[CHUNKS_COLLECTION]

    await documents.create_index(
        "content_hash",
        unique=True,
    )

    await chunks.create_index(
        "document_id",
    )