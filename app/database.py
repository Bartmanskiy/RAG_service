from pymongo import AsyncMongoClient

from app.config import settings


client = AsyncMongoClient(settings.mongo_url)
database = client[settings.mongo_db]

DOCUMENTS_COLLECTION = "documents"
CHUNKS_COLLECTION = "chunks"


async def get_database():
    return database