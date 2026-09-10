import json

from app.core.redis import redis_client


NOTIFICATION_QUEUE = "foodflow:queue:notifications"


class Queue:

    @staticmethod
    def enqueue(payload: dict) -> None:
        redis_client.rpush(
            NOTIFICATION_QUEUE,
            json.dumps(payload),
        )

    @staticmethod
    def dequeue() -> dict | None:
        value = redis_client.lpop(NOTIFICATION_QUEUE)

        if value is None:
            return None

        return json.loads(value)