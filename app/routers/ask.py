from fastapi import APIRouter, Depends

from app.dependencies import get_rag_service
from app.schemas.ask import AskRequest, AskResponse
from app.services.rag_service import RAGService


router = APIRouter(
    prefix="/api/ask",
    tags=["Ask"],
)


@router.post(
    "",
    response_model=AskResponse,
)
async def ask_question(
    request: AskRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    return await rag_service.answer(
        question=request.question,
        top_k=request.top_k,
        document_ids=request.document_ids,
    )