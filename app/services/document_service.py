import hashlib

from fastapi import HTTPException, UploadFile, status, BackgroundTasks
from bson import ObjectId

from pymongo.errors import DuplicateKeyError

from app.config import settings
from app.models.document import create_document
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas import document


ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}


class DocumentService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        chunk_repository: ChunkRepository,
    ):
        self.document_repository = document_repository
        self.chunk_repository = chunk_repository

    async def create_document(
        self,
        file: UploadFile,
        background_tasks: BackgroundTasks,
        ingestion_service,
    ) -> dict:
        filename = file.filename or ""

        extension = (
            "." + filename.rsplit(".", 1)[-1].lower()
            if "." in filename
            else ""
        )

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported file type",
            )

        content = await file.read()

        if len(content) > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File is too large",
            )

        content_hash = hashlib.sha256(content).hexdigest()

        existing_document = (
            await self.document_repository.get_by_content_hash(
                content_hash
            )
        )

        if existing_document is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document already exists",
            )

        document = create_document(
            filename=filename,
            content_hash=content_hash,
        )

        try:
            await self.document_repository.create(document)
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document already exists",
            )

        background_tasks.add_task(
            ingestion_service.process_document,
            document["_id"],
            filename,
            content,
        )

        return document

    async def get_document(
        self,
        document_id: str,
    ) -> dict:
        try:
            object_id = ObjectId(document_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        document = await self.document_repository.get_by_id(object_id)

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        return document

    async def get_documents(self) -> list[dict]:
        return await self.document_repository.get_all()

    async def delete_document(
        self,
        document_id: str,
    ) -> None:
        try:
            object_id = ObjectId(document_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        document = await self.document_repository.get_by_id(object_id)

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        await self.chunk_repository.delete_by_document_id(object_id)
        await self.document_repository.delete(object_id)



