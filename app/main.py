import time
from datetime import datetime
from typing import List
from uuid import uuid4
import random
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.market_data import BASE_MARKET_DATA, get_all_market_data, get_market_data
from app.matching_engine import determine_order_status
from app.models import Order, OrderEvent
from app.schemas import OrderCreate, OrderEventResponse, OrderResponse
from app.event_publisher import get_recent_queued_order_events, publish_order_events
from app.redis_client import check_redis_connection

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TradePulse",
    description="Trading Support / Production Monitoring API",
    version="0.6.0"
)

HTTP_REQUESTS_TOTAL = Counter(
    "tradepulse_http_requests_total",
    "Total HTTP requests received by TradePulse",
    ["method", "endpoint", "http_status"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "tradepulse_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

ORDERS_CREATED_TOTAL = Counter(
    "tradepulse_orders_created_total",
    "Total orders created by TradePulse",
    ["source", "status", "symbol"]
)

ORDER_EVENTS_CREATED_TOTAL = Counter(
    "tradepulse_order_events_created_total",
    "Total order lifecycle events created",
    ["event_type"]
)

def normalize_path(path: str) -> str:
    if path.startswith("/orders/") and path.endswith("/events"):
        return "/orders/{order_id}/events"

    if path.startswith("/orders/"):
        return "/orders/{order_id}"

    return path

@app.middleware("http")
async def collect_http_metrics(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time
    endpoint = normalize_path(request.url.path)

    HTTP_REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=endpoint,
        http_status=str(response.status_code)
    ).inc()

    HTTP_REQUEST_DURATION_SECONDS.labels(
        method=request.method,
        endpoint=endpoint
    ).observe(duration)

    return response

REDIS_UP = Gauge(
    "tradepulse_redis_up",
    "Redis health status. 1 means up, 0 means down."
)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


def create_order_events(db: Session, order_id: str, final_status: str):
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


@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": "tradepulse-api",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/redis/health")
def redis_health_check():
    redis_is_up = check_redis_connection()
    REDIS_UP.set(1 if redis_is_up else 0)

    if redis_is_up:
        return {
            "status": "UP",
            "service": "tradepulse-redis"
        }

    return {
        "status": "DOWN",
        "service": "tradepulse-redis"
    }

@app.get("/queue/order-events")
def get_queued_order_events(limit: int = 10):
    return {
        "stream": "tradepulse:order_events",
        "limit": limit,
        "events": get_recent_queued_order_events(limit)
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
    events = create_order_events(db, new_order.order_id, status)
    db.commit()
    db.refresh(new_order)

    ORDERS_CREATED_TOTAL.labels(
        source="api",
        status=new_order.status,
        symbol=new_order.symbol
    ).inc()

    for event in events:
        ORDER_EVENTS_CREATED_TOTAL.labels(
            event_type=event.event_type
        ).inc()

    publish_order_events(new_order, events)

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


@app.get("/orders/{order_id}/events", response_model=List[OrderEventResponse])
def get_order_events(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return (
        db.query(OrderEvent)
        .filter(OrderEvent.order_id == order_id)
        .order_by(OrderEvent.created_at.asc())
        .all()
    )

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
    events = create_order_events(db, simulated_order.order_id, status)
    db.commit()
    db.refresh(simulated_order)

    ORDERS_CREATED_TOTAL.labels(
        source="simulator",
        status=simulated_order.status,
        symbol=simulated_order.symbol
    ).inc()

    for event in events:
        ORDER_EVENTS_CREATED_TOTAL.labels(
            event_type=event.event_type
        ).inc()

    publish_order_events(simulated_order, events)

    return simulated_order