from pymongo.asynchronous.database import AsyncDatabase

from app.database import CHUNKS_COLLECTION


VECTOR_INDEX_NAME = "vector_index"


async def init_vector_index(db: AsyncDatabase) -> None:
    chunks = db[CHUNKS_COLLECTION]

    existing_indexes = await (await chunks.list_search_indexes()).to_list()

    if any(index["name"] == VECTOR_INDEX_NAME for index in existing_indexes):
        return

    await chunks.create_search_index(
        {
            "name": VECTOR_INDEX_NAME,
            "type": "vectorSearch",
            "definition": {
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": 768,
                        "similarity": "cosine",
                    },
                    {
                        "type": "filter",
                        "path": "document_id",
                    },
                ]
            },
        }
    )