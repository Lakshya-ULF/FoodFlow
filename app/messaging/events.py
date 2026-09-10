from dataclasses import dataclass, asdict


@dataclass
class OrderStatusChangedEvent:
    order_id: int
    user_id: int
    status: str

    @property
    def event_type(self) -> str:
        return "order.status_changed"

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            **asdict(self),
        }