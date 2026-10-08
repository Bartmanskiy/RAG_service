from fastapi import Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.database import get_database
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository


def get_document_repository(
    db: AsyncDatabase = Depends(get_database),
) -> DocumentRepository:
    return DocumentRepository(db)


def get_chunk_repository(
    db: AsyncDatabase = Depends(get_database),
) -> ChunkRepository:
    return ChunkRepository(db)