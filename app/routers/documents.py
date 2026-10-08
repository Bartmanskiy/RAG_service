from fastapi import APIRouter, Depends, File, UploadFile, status, BackgroundTasks

from app.dependencies import get_document_service, get_ingestion_service
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


def document_to_response(document: dict) -> DocumentResponse:
    return DocumentResponse(
        id=str(document["_id"]),
        filename=document["filename"],
        status=document["status"],
        chunks_count=document["chunks_count"],
        created_at=document["created_at"],
    )


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service),
    ingestion_service=Depends(get_ingestion_service),
):
    document = await service.create_document(
        file=file,
        background_tasks=background_tasks,
        ingestion_service=ingestion_service,
    )

    return document_to_response(document)


@router.get(
    "",
    response_model=list[DocumentResponse],
)
async def get_documents(
    service: DocumentService = Depends(get_document_service),
):
    documents = await service.get_documents()

    return [
        document_to_response(document)
        for document in documents
    ]


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
):
    document = await service.get_document(document_id)

    return document_to_response(document)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
):
    await service.delete_document(document_id)

