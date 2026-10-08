from fastapi import Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.database import get_database
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository

from app.services.document_service import DocumentService
from app.services.ingestion_service import IngestionService

from app.clients.ollama_client import OllamaClient


def get_document_repository(
    db: AsyncDatabase = Depends(get_database),
) -> DocumentRepository:
    return DocumentRepository(db)


def get_chunk_repository(
    db: AsyncDatabase = Depends(get_database),
) -> ChunkRepository:
    return ChunkRepository(db)



def get_document_service(
    document_repository: DocumentRepository = Depends(
        get_document_repository
    ),
    chunk_repository: ChunkRepository = Depends(
        get_chunk_repository
    ),
) -> DocumentService:
    return DocumentService(
        document_repository=document_repository,
        chunk_repository=chunk_repository,
    )


def get_ollama_client() -> OllamaClient:
    return OllamaClient()


def get_ingestion_service(
    document_repository: DocumentRepository = Depends(
        get_document_repository
    ),
    chunk_repository: ChunkRepository = Depends(
        get_chunk_repository
    ),
    ollama_client: OllamaClient = Depends(
        get_ollama_client
    ),
) -> IngestionService:
    return IngestionService(
        document_repository=document_repository,
        chunk_repository=chunk_repository,
        embedding_client=ollama_client,
    )
