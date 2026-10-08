from bson import ObjectId

from app.config import settings
from app.repositories.chunk_repository import ChunkRepository

from bson.errors import InvalidId


class RetrievalService:
    def __init__(
        self,
        chunk_repository: ChunkRepository,
        embedding_client,
    ):
        self.chunk_repository = chunk_repository
        self.embedding_client = embedding_client

    async def search(
        self,
        question: str,
        top_k: int | None = None,
        document_ids: list[str] | None = None,
    ) -> list[dict]:
        query_vector = await self.embedding_client.embed(question)

        limit = top_k or settings.top_k

        object_ids = None

        if document_ids:
            try:
                object_ids = [
                    ObjectId(document_id)
                    for document_id in document_ids
                ]
            except InvalidId:
                raise ValueError("Invalid document_id")

        results = await self.chunk_repository.vector_search(
            query_vector=query_vector,
            top_k=limit,
            document_ids=object_ids,
        )

        return [
            result
            for result in results
            if result["score"] >= settings.score_threshold
        ]