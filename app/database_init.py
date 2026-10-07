from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import CollectionInvalid

from app.database import DOCUMENTS_COLLECTION, CHUNKS_COLLECTION


async def create_collection_if_not_exists(
    db: AsyncDatabase,
    collection_name: str,
) -> None:
    if collection_name not in await db.list_collection_names():
        try:
            await db.create_collection(collection_name)
        except CollectionInvalid:
            pass


async def init_database(db: AsyncDatabase) -> None:
    await create_collection_if_not_exists(db, DOCUMENTS_COLLECTION)
    await create_collection_if_not_exists(db, CHUNKS_COLLECTION)