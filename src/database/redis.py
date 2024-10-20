import redis.asyncio as redis

from src.conf.config import settings

redis_db = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password
)
