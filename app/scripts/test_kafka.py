from app.messaging.producer import publish_event
from app.messaging.topics import ORDER_EVENTS_TOPIC


event = {
    "event_type": "order.status_changed",
    "order_id": 123,
    "user_id": 42,
    "status": "preparing",
}

publish_event(
    ORDER_EVENTS_TOPIC,
    event,
)

print("Event published")