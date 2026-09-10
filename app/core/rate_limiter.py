from fastapi import HTTPException, Request

from app.core.redis import redis_client


RATE_LIMIT = 100
WINDOW_SECONDS = 60


def rate_limit(request: Request):
    client_ip = request.client.host

    key = f"rate_limit:{client_ip}"

    count = redis_client.incr(key)

    if count == 1:
        redis_client.expire(key, WINDOW_SECONDS)

    if count > RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
        )