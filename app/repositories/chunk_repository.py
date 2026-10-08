from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.database import CHUNKS_COLLECTION


class ChunkRepository:
    def __init__(self, db: AsyncDatabase):
        self.collection = db[CHUNKS_COLLECTION]

    async def create_many(self, chunks: list[dict]) -> int:
        if not chunks:
            return 0

        result = await self.collection.insert_many(chunks)
        return len(result.inserted_ids)

    async def get_by_document_id(
        self,
        document_id: ObjectId,
    ) -> list[dict]:
        cursor = self.collection.find(
            {"document_id": document_id}
        ).sort("chunk_index", 1)

        return await cursor.to_list()

    async def delete_by_document_id(
        self,
        document_id: ObjectId,
    ) -> int:
        result = await self.collection.delete_many(
            {"document_id": document_id}
        )

        return result.deleted_count

    async def vector_search(
        self,
        query_vector: list[float],
        top_k: int,
        document_ids: list[ObjectId] | None = None,
    ) -> list[dict]:
        vector_search_stage = {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": max(top_k * 10, 50),
                "limit": top_k,
            }
        }

        if document_ids:
            vector_search_stage["$vectorSearch"]["filter"] = {
                "document_id": {
                    "$in": document_ids,
                }
            }

        pipeline = [
            vector_search_stage,
            {
                "$addFields": {
                    "score": {
                        "$meta": "vectorSearchScore",
                    }
                }
            },
            {
                "$lookup": {
                    "from": "documents",
                    "localField": "document_id",
                    "foreignField": "_id",
                    "as": "document",
                    }
                },
            {
                "$unwind": "$document",
            },
        ]

        cursor = await self.collection.aggregate(pipeline)

        return await cursor.to_list()