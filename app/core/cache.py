import json
from typing import Any
from prometheus_client import Counter
from app.core.redis import redis_client
import logging
import redis

logger = logging.getLogger(__name__)

cache_hits = Counter(
    "foodflow_cache_hits_total",
    "Total number of Redis cache hits",
)

cache_misses = Counter(
    "foodflow_cache_misses_total",
    "Total number of Redis cache misses",
)

class Cache:
    @staticmethod
    def get(key):
        try:
            value = redis_client.get(key)

            if value is None:
                cache_misses.inc()
                return None

            cache_hits.inc()
            return json.loads(value)

        except redis.RedisError:
            logger.exception("Redis cache read failed")
            return None

    @staticmethod
    def set(key, value, ttl=60):
        try:
            redis_client.setex(
                key,
                ttl,
                json.dumps(value),
            )
        except redis.RedisError:
            logger.exception("Redis cache write failed")

    @staticmethod
    def delete(key):
        try:
            redis_client.delete(key)
        except redis.RedisError:
            logger.exception("Redis cache delete failed")