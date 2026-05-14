from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4
from typing import Dict, List
import random

app = FastAPI(
    title="TradePulse",
    description="Trading Support / Production Monitoring API",
    version="0.1.0"
)

orders: Dict[str, dict] = {}


class OrderCreate(BaseModel):
    symbol: str
    side: str
    quantity: int
    price: float
    trader: str


class OrderResponse(BaseModel):
    order_id: str
    symbol: str
    side: str
    quantity: int
    price: float
    trader: str
    status: str
    created_at: str


@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": "tradepulse-api",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/orders", response_model=OrderResponse)
def create_order(order: OrderCreate):
    order_id = str(uuid4())

    new_order = {
        "order_id": order_id,
        "symbol": order.symbol.upper(),
        "side": order.side.upper(),
        "quantity": order.quantity,
        "price": order.price,
        "trader": order.trader,
        "status": "NEW",
        "created_at": datetime.utcnow().isoformat()
    }

    orders[order_id] = new_order
    return new_order


@app.get("/orders", response_model=List[OrderResponse])
def get_orders():
    return list(orders.values())


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")

    return orders[order_id]


@app.post("/simulate/order", response_model=OrderResponse)
def simulate_order():
    symbols = ["AAPL", "MSFT", "TSLA", "NVDA", "UST10Y", "EURUSD", "BTCUSD"]
    sides = ["BUY", "SELL"]
    traders = ["trader_nyc_01", "trader_ldn_02", "trader_tokyo_03"]

    order_id = str(uuid4())

    simulated_order = {
        "order_id": order_id,
        "symbol": random.choice(symbols),
        "side": random.choice(sides),
        "quantity": random.randint(100, 10000),
        "price": round(random.uniform(90, 500), 2),
        "trader": random.choice(traders),
        "status": random.choice(["NEW", "ACKED", "FILLED", "REJECTED"]),
        "created_at": datetime.utcnow().isoformat()
    }

    orders[order_id] = simulated_order
    return simulated_order