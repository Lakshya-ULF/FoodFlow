import json
import time

from prometheus_client import Counter, Histogram
from kafka import KafkaProducer

from app.core.config import settings


producer = KafkaProducer(
    bootstrap_servers=settings.kafka_bootstrap_servers,
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
)


kafka_events_published = Counter(
    "foodflow_kafka_events_published_total",
    "Total number of Kafka events successfully published",
)

kafka_events_failed = Counter(
    "foodflow_kafka_events_failed_total",
    "Total number of Kafka events that failed to publish",
)

kafka_publish_latency = Histogram(
    "foodflow_kafka_publish_latency_seconds",
    "Time taken to successfully publish a Kafka event",
)


def publish_event(
    topic: str,
    event: dict,
) -> None:
    start_time = time.perf_counter()

    try:
        future = producer.send(
            topic,
            value=event,
        )

        future.get(timeout=10)

        kafka_events_published.inc()

        kafka_publish_latency.observe(
            time.perf_counter() - start_time
        )

    except Exception:
        kafka_events_failed.inc()
        raise