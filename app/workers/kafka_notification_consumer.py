import logging
import time

from prometheus_client import Counter, Histogram, start_http_server
from sqlalchemy import select

from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.models.processed_event import ProcessedEvent
from app.services.notification_service import NotificationService

from app.messaging.consumer import consumer


setup_logging()

logger = logging.getLogger(__name__)


kafka_events_processed = Counter(
    "foodflow_kafka_events_processed_total",
    "Total number of Kafka events successfully processed",
)

kafka_events_processing_failed = Counter(
    "foodflow_kafka_events_processing_failed_total",
    "Total number of Kafka events that failed during processing",
)

kafka_events_duplicate = Counter(
    "foodflow_kafka_events_duplicate_total",
    "Total number of duplicate Kafka events skipped",
)

kafka_consumer_processing_latency = Histogram(
    "foodflow_kafka_consumer_processing_seconds",
    "Time taken to process a Kafka event",
)


def process_event(event: dict) -> None:
    if event.get("event_type") != "order.status_changed":
        return

    event_id = event["event_id"]

    db = SessionLocal()

    try:
        # Check whether this event was already processed
        existing_event = db.scalar(
            select(ProcessedEvent).where(
                ProcessedEvent.event_id == event_id
            )
        )

        if existing_event is not None:
            kafka_events_duplicate.inc()

            logger.info(
                "Event already processed. Skipping: event_id=%s",
                event_id,
            )
            return

        service = NotificationService(db)

        status = event["status"]

        messages = {
            "paid": "Your payment was successful.",
            "restaurant_accepted": "Your order has been accepted by the restaurant.",
            "preparing": "Your order is being prepared.",
            "ready_for_pickup": "Your order is ready for pickup.",
            "picked_up": "Your order has been picked up by the delivery partner.",
            "out_for_delivery": "Your order is out for delivery.",
            "delivered": "Your order has been delivered.",
            "cancelled": "Your order has been cancelled.",
            "payment_failed": "Your payment failed.",
        }

        message = messages.get(status)

        if message is None:
            return

        service.create_notification(
            user_id=event["user_id"],
            order_id=event["order_id"],
            notification_type="order_status",
            message=message,
        )

        # Record the event as processed
        db.add(
            ProcessedEvent(
                event_id=event_id,
                event_type=event["event_type"],
            )
        )

        # Both operations commit together
        db.commit()

        logger.info(
            "Processed event: notification created for order_id=%s event_id=%s",
            event["order_id"],
            event_id,
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def run():
    logger.info("Kafka notification consumer started...")

    # Expose Prometheus metrics for this worker process
    start_http_server(8002)

    for message in consumer:
        event = message.value

        start_time = time.perf_counter()

        try:
            process_event(event)

            consumer.commit()

            kafka_events_processed.inc()

            kafka_consumer_processing_latency.observe(
                time.perf_counter() - start_time
            )

        except Exception:
            kafka_events_processing_failed.inc()

            logger.exception(
                "Failed to process Kafka event"
            )


if __name__ == "__main__":
    run()