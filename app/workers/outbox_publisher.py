import json
import time
from app.core.constants import OutboxStatus
from app.core.queue import Queue
from app.db.session import SessionLocal
from app.repositories.outbox_repository import OutboxRepository
from app.messaging.producer import publish_event
from app.messaging.topics import ORDER_EVENTS_TOPIC
from prometheus_client import start_http_server

def publish_pending_events():
    db = SessionLocal()

    try:
        repository = OutboxRepository(db)
        events = repository.get_pending(limit=10)

        for event in events:
            try:
                payload = json.loads(event.payload)

                # Redis notification queue
                Queue.enqueue(payload)

                # Kafka order event
                if event.event_type == "order_status_notification":
                    kafka_event = {
                        "event_id": event.id,
                        "event_type": "order.status_changed",
                        "order_id": payload["order_id"],
                        "user_id": payload["user_id"],
                        "status": payload["status"],
                    }

                    publish_event(
                        ORDER_EVENTS_TOPIC,
                        kafka_event,
                    )

                event.status = "published"
                event.last_error = None

            except Exception as exc:
                event.retry_count += 1
                event.last_error = str(exc)

                if event.retry_count >= OutboxStatus.MAX_RETRIES:
                    event.status = OutboxStatus.DEAD_LETTER

                    print(
                        f"Outbox event moved to dead letter: "
                        f"id={event.id}, "
                        f"retries={event.retry_count}"
                    )
                else:
                    print(
                        f"Failed to publish outbox event "
                        f"id={event.id}, "
                        f"retry={event.retry_count}, "
                        f"error={exc}"
                    )

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

def run_publisher():
    print("Outbox publisher started...")

    start_http_server(8001)

    while True:
        try:
            publish_pending_events()
        except Exception as exc:
            print(f"Failed to publish outbox events: {exc}")

        time.sleep(1)


if __name__ == "__main__":
    run_publisher()