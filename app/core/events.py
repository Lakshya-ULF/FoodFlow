from app.core.kafka import producer


def publish_event(
    topic: str,
    event: dict,
) -> None:
    producer.send(
        topic,
        value=event,
    )