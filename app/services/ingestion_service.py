from bson import ObjectId

from app.models.chunk import create_chunk
from app.parsers.parser import parse_document
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.chunking_service import chunk_pages


class IngestionService:

    def __init__(
        self,
        document_repository: DocumentRepository,
        chunk_repository: ChunkRepository,
        embedding_client,
    ):
        self.document_repository = document_repository
        self.chunk_repository = chunk_repository
        self.embedding_client = embedding_client

    async def process_document(
        self,
        document_id: ObjectId,
        filename: str,
        content: bytes,
    ) -> None:
        try:
            pages = parse_document(
                filename=filename,
                content=content,
            )

            chunks = chunk_pages(pages)

            if not chunks:
                raise ValueError(
                    "Document contains no text"
            )

            documents = []

            for chunk in chunks:
                embedding = await self.embedding_client.embed(
                    chunk["text"]
                )

                documents.append(
                    create_chunk(
                        document_id=document_id,
                        text=chunk["text"],
                        embedding=embedding,
                        page=chunk["page"],
                        chunk_index=chunk["chunk_index"],
                    )
                )

            chunks_count = await self.chunk_repository.create_many(
                documents
                )

            await self.document_repository.update_chunks_count(
                document_id=document_id,
                chunks_count=chunks_count,
            )

            await self.document_repository.update_status(
                document_id=document_id,
                status="ready",
            )

        except Exception as error:
            await self.document_repository.update_status(
                document_id=document_id,
                status="failed",
                error=str(error),
            )