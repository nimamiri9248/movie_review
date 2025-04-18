from redis import Redis
from redis.asyncio import from_url

from src.core.config import settings


redis_cli = None


async def get_redis_client() -> Redis:
    global redis_cli
    if redis_cli is None:
        redis_cli = await from_url(settings.redis_url, decode_responses=True)
    return redis_cli
