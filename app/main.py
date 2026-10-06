from fastapi import FastAPI

from app.config import settings


app = FastAPI(title="Corporate Knowledge RAG")


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
    }