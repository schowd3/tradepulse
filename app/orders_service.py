from uuid import uuid4
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models import Order, OrderEvent
from app.matching_engine import determine_order_status
from app.metrics import ORDERS_CREATED_TOTAL, ORDER_EVENTS_CREATED_TOTAL
from app.event_publisher import publish_order_events

def create_order_events(db: Session, order_id: str, final_status: str) -> List[OrderEvent]:
    events = [
        OrderEvent(
            event_id=str(uuid4()),
            order_id=order_id,
            event_type="ORDER_RECEIVED",
            message="Order received by TradePulse API",
            created_at=datetime.utcnow()
        )
    ]

    if final_status == "ACKED":
        events.append(
            OrderEvent(
                event_id=str(uuid4()),
                order_id=order_id,
                event_type="ORDER_ACKED",
                message="Order accepted by simulated venue",
                created_at=datetime.utcnow()
            )
        )

    elif final_status == "FILLED":
        events.append(
            OrderEvent(
                event_id=str(uuid4()),
                order_id=order_id,
                event_type="ORDER_ACKED",
                message="Order accepted by simulated venue",
                created_at=datetime.utcnow()
            )
        )
        events.append(
            OrderEvent(
                event_id=str(uuid4()),
                order_id=order_id,
                event_type="ORDER_FILLED",
                message="Order filled based on simulated market data",
                created_at=datetime.utcnow()
            )
        )

    elif final_status == "REJECTED":
        events.append(
            OrderEvent(
                event_id=str(uuid4()),
                order_id=order_id,
                event_type="ORDER_REJECTED",
                message="Order rejected by simulated matching engine",
                created_at=datetime.utcnow()
            )
        )

    db.add_all(events)
    return events


def create_and_publish_order(
    db: Session,
    symbol: str,
    side: str,
    quantity: int,
    price: float,
    trader: str,
    source: str
) -> Order:
    # 1. Determine status
    status = determine_order_status(
        symbol=symbol,
        side=side,
        price=price
    )

    # 2. Instantiate and save Order
    new_order = Order(
        order_id=str(uuid4()),
        symbol=symbol.upper(),
        side=side.upper(),
        quantity=quantity,
        price=price,
        trader=trader,
        status=status,
        created_at=datetime.utcnow()
    )
    db.add(new_order)

    # 3. Create events
    events = create_order_events(db, new_order.order_id, status)

    # 4. Commit transaction
    db.commit()
    db.refresh(new_order)

    # 5. Record Metrics
    ORDERS_CREATED_TOTAL.labels(
        source=source,
        status=new_order.status,
        symbol=new_order.symbol
    ).inc()

    for event in events:
        ORDER_EVENTS_CREATED_TOTAL.labels(
            event_type=event.event_type
        ).inc()

    # 6. Publish to event queue (best-effort)
    publish_order_events(new_order, events)

    return new_order
