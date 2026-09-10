import redis

from app.core.config import settings

if settings.redis_url:
    redis_client = redis.Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )
else:
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,
    )