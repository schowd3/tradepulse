from datetime import datetime
from typing import List
from uuid import uuid4
import random

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Order
from app.schemas import OrderCreate, OrderResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TradePulse",
    description="Trading Support / Production Monitoring API",
    version="0.3.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": "tradepulse-api",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/orders", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    new_order = Order(
        order_id=str(uuid4()),
        symbol=order.symbol.upper(),
        side=order.side.upper(),
        quantity=order.quantity,
        price=order.price,
        trader=order.trader,
        status="NEW",
        created_at=datetime.utcnow()
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


@app.get("/orders", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.created_at.desc()).all()


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@app.post("/simulate/order", response_model=OrderResponse)
def simulate_order(db: Session = Depends(get_db)):
    symbols = ["AAPL", "MSFT", "TSLA", "NVDA", "UST10Y", "EURUSD", "BTCUSD"]
    sides = ["BUY", "SELL"]
    traders = ["trader_nyc_01", "trader_ldn_02", "trader_tokyo_03"]

    simulated_order = Order(
        order_id=str(uuid4()),
        symbol=random.choice(symbols),
        side=random.choice(sides),
        quantity=random.randint(100, 10000),
        price=round(random.uniform(90, 500), 2),
        trader=random.choice(traders),
        status=random.choice(["NEW", "ACKED", "FILLED", "REJECTED"]),
        created_at=datetime.utcnow()
    )

    db.add(simulated_order)
    db.commit()
    db.refresh(simulated_order)

    return simulated_order