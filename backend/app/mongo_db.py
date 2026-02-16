from motor.motor_asyncio import AsyncIOMotorClient
from .settings import settings

client: AsyncIOMotorClient | None = None

def get_collection():
    if client is None:
        raise RuntimeError("Mongo client not initialized")
    db = client[settings.MONGO_DB]
    return db[settings.MONGO_COLLECTION]

async def init_mongo():
    global client
    client = AsyncIOMotorClient(settings.MONGO_URI)
    col = get_collection()
    # Ensure uniqueness at DB level [web:187]
    await col.create_index("code", unique=True)
    await col.create_index("long_url", unique=True)
