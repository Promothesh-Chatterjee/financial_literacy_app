import aioredis
from .config import settings

redis = None

async def get_redis() -> aioredis.Redis | None:
    global redis
    if redis is None:
        try:
            redis = aioredis.from_url(settings.redis_url, decode_responses=True)
        except Exception:
            redis = None
    return redis
