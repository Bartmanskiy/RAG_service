from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=1000,
    )
    document_ids: list[str] | None = None
    top_k: int | None = Field(
        default=None,
        ge=1,
        le=10,
    )


class SourceResponse(BaseModel):
    document_id: str
    filename: str
    page: int | None
    score: float
    snippet: str


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]