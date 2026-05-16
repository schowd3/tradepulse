from datetime import datetime
from typing import List
from uuid import uuid4
import random

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.market_data import BASE_MARKET_DATA, get_all_market_data, get_market_data
from app.matching_engine import determine_order_status
from app.models import Order
from app.schemas import OrderCreate, OrderResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TradePulse",
    description="Trading Support / Production Monitoring API",
    version="0.4.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": "tradepulse-api",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/market-data")
def market_data():
    return get_all_market_data()


@app.get("/market-data/{symbol}")
def market_data_by_symbol(symbol: str):
    data = get_market_data(symbol)

    if data is None:
        raise HTTPException(status_code=404, detail="Market data not found for symbol")

    return data


@app.post("/orders", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    status = determine_order_status(
        symbol=order.symbol,
        side=order.side,
        price=order.price
    )

    new_order = Order(
        order_id=str(uuid4()),
        symbol=order.symbol.upper(),
        side=order.side.upper(),
        quantity=order.quantity,
        price=order.price,
        trader=order.trader,
        status=status,
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
    symbols = list(BASE_MARKET_DATA.keys())
    sides = ["BUY", "SELL"]
    traders = ["trader_nyc_01", "trader_ldn_02", "trader_tokyo_03"]

    symbol = random.choice(symbols)
    side = random.choice(sides)
    market = get_market_data(symbol)

    if side == "BUY":
        price = round(random.uniform(market.bid, market.ask + 1), 4)
    else:
        price = round(random.uniform(market.bid - 1, market.ask), 4)

    status = determine_order_status(
        symbol=symbol,
        side=side,
        price=price
    )

    simulated_order = Order(
        order_id=str(uuid4()),
        symbol=symbol,
        side=side,
        quantity=random.randint(100, 10000),
        price=price,
        trader=random.choice(traders),
        status=status,
        created_at=datetime.utcnow()
    )

    db.add(simulated_order)
    db.commit()
    db.refresh(simulated_order)

    return simulated_order