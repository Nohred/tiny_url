import redis.asyncio as redis
from .settings import settings

r: redis.Redis | None = None

async def init_redis():
    global r
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_redis():
    if r is None:
        raise RuntimeError("Redis client not initialized")
    return r
