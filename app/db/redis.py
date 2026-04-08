import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import settings

redis: Redis = None


async def connect_to_redis():
    global redis
    redis = await aioredis.from_url(settings.redis_url)
    print("Connected to Redis")


async def close_redis_connection():
    global redis
    if redis:
        await redis.close()
        print("Disconnected from Redis")


def get_redis() -> Redis:
    return redis
