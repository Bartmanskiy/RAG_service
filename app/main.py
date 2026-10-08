from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pymongo.asynchronous.database import AsyncDatabase

from app.config import settings
from app.database import database, get_database
from app.database_init import init_database
from app.database_indexes import init_indexes
from app.vector_index import init_vector_index
from app.routers.documents import router as documents_router
from app.routers.ask import router as ask_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database(database)
    await init_indexes(database)
    await init_vector_index(database)
    yield

app = FastAPI(
title="Corporate Knowledge RAG",
lifespan=lifespan,
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

app.include_router(documents_router)
app.include_router(ask_router)

@app.get("/")
async def home():
    return FileResponse("app/static/index.html")

@app.get("/health")
async def health_check(
    db: AsyncDatabase = Depends(get_database),
    ):
    await db.command("ping")


    return {
        "status": "ok",
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
        "mongodb": "ok",
    }

