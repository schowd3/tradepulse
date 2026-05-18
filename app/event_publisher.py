from typing import Iterable

import redis

from app.models import Order, OrderEvent
from app.redis_client import redis_client

ORDER_EVENTS_STREAM = "tradepulse:order_events"


def publish_order_events(order: Order, events: Iterable[OrderEvent]) -> None:
    """
    Publish order lifecycle events to a Redis Stream.

    This is intentionally best-effort. If Redis is down, the order is still
    saved in PostgreSQL and the API response should not fail.
    """
    try:
        for event in events:
            redis_client.xadd(
                ORDER_EVENTS_STREAM,
                {
                    "event_id": event.event_id,
                    "order_id": event.order_id,
                    "event_type": event.event_type,
                    "message": event.message,
                    "order_status": order.status,
                    "symbol": order.symbol,
                    "side": order.side,
                    "quantity": str(order.quantity),
                    "price": str(order.price),
                    "trader": order.trader,
                    "created_at": event.created_at.isoformat(),
                },
                maxlen=1000,
                approximate=True,
            )
    except redis.RedisError as exc:
        print(f"WARNING: Failed to publish order events to Redis: {exc}")


def get_recent_queued_order_events(limit: int = 10):
    try:
        entries = redis_client.xrevrange(
            ORDER_EVENTS_STREAM,
            count=limit
        )

        return [
            {
                "redis_id": redis_id,
                **fields
            }
            for redis_id, fields in entries
        ]

    except redis.RedisError as exc:
        print(f"WARNING: Failed to read Redis stream: {exc}")
        return []