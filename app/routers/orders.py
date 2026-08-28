from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order, OrderEvent
from app.schemas import OrderCreate, OrderResponse, OrderEventResponse
from app.orders_service import create_and_publish_order
from app.simulator import simulate_random_order
from app.event_publisher import get_recent_queued_order_events

router = APIRouter()


@router.post("/orders", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)) -> Order:
    return create_and_publish_order(
        db=db,
        symbol=order.symbol,
        side=order.side,
        quantity=order.quantity,
        price=order.price,
        trader=order.trader,
        source="api"
    )


@router.get("/orders", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db)) -> List[Order]:
    return db.query(Order).order_by(Order.created_at.desc()).all()


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db)) -> Order:
    order = db.query(Order).filter(Order.order_id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@router.get("/orders/{order_id}/events", response_model=List[OrderEventResponse])
def get_order_events(order_id: str, db: Session = Depends(get_db)) -> List[OrderEvent]:
    order = db.query(Order).filter(Order.order_id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return (
        db.query(OrderEvent)
        .filter(OrderEvent.order_id == order_id)
        .order_by(OrderEvent.created_at.asc())
        .all()
    )


@router.post("/simulate/order", response_model=OrderResponse)
def simulate_order(db: Session = Depends(get_db)) -> Order:
    return simulate_random_order(db)


@router.get("/queue/order-events")
def get_queued_order_events(limit: int = 10) -> dict:
    return {
        "stream": "tradepulse:order_events",
        "limit": limit,
        "events": get_recent_queued_order_events(limit)
    }
