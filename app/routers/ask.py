from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

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
    try:
        return await rag_service.answer(
            question=request.question,
            top_k=request.top_k,
            document_ids=request.document_ids,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.get(
    "/stream",
)
async def stream_question(
    question: str = Query(..., min_length=3, max_length=1000),
    top_k: int | None = Query(None, ge=1, le=10),
    document_ids: list[str] | None = Query(None),
    rag_service: RAGService = Depends(get_rag_service),
):
    return StreamingResponse(
        rag_service.stream_answer(
            question=question,
            top_k=top_k,
            document_ids=document_ids,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )