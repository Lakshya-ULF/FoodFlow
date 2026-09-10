import json

from kafka import KafkaConsumer

from app.messaging.topics import ORDER_EVENTS_TOPIC
from app.core.config import settings


consumer = KafkaConsumer(
    ORDER_EVENTS_TOPIC,
    bootstrap_servers=settings.kafka_bootstrap_servers,
    group_id="foodflow-notification-consumer",
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    value_deserializer=lambda value: json.loads(value.decode("utf-8")),
)