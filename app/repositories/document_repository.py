from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.database import DOCUMENTS_COLLECTION


class DocumentRepository:
    def __init__(self, db: AsyncDatabase):
        self.collection = db[DOCUMENTS_COLLECTION]

    async def create(self, document: dict) -> ObjectId:
        result = await self.collection.insert_one(document)
        return result.inserted_id

    async def get_by_id(self, document_id: ObjectId) -> dict | None:
        return await self.collection.find_one({"_id": document_id})

    async def get_by_content_hash(self, content_hash: str) -> dict | None:
        return await self.collection.find_one(
            {"content_hash": content_hash}
        )

    async def get_all(self) -> list[dict]:
        cursor = self.collection.find().sort("created_at", -1)
        return await cursor.to_list()

    async def update_status(
        self,
        document_id: ObjectId,
        status: str,
        error: str | None = None,
    ) -> None:
        update = {"status": status}

        if error is not None:
            update["error"] = error

        await self.collection.update_one(
            {"_id": document_id},
            {"$set": update},
        )

    async def update_chunks_count(
        self,
        document_id: ObjectId,
        chunks_count: int,
    ) -> None:
        await self.collection.update_one(
            {"_id": document_id},
            {"$set": {"chunks_count": chunks_count}},
        )

    async def delete(self, document_id: ObjectId) -> None:
        await self.collection.delete_one(
            {"_id": document_id}
        )