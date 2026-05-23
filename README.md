# TradePulse

TradePulse is a production-style trading support and monitoring application built to simulate order flow, expose support APIs, and demonstrate cloud-native deployment practices.

The project models a simplified trading support workflow where orders are created, evaluated against simulated market data, persisted to PostgreSQL, published to Redis as lifecycle events, and monitored through Prometheus metrics.

## Current Features

- FastAPI backend
- Swagger API documentation
- Order creation API
- Simulated trade/order event generator
- PostgreSQL persistence
- SQLAlchemy ORM models
- Market data simulator with bid/ask prices
- Basic order status engine
  - BUY orders fill when price crosses the ask
  - SELL orders fill when price crosses the bid
  - Unsupported symbols are rejected
- Order lifecycle event tracking
  - ORDER_RECEIVED
  - ORDER_ACKED
  - ORDER_FILLED
  - ORDER_REJECTED
- Redis event queue using Redis Streams
- Docker Compose local environment
- Health check endpoints
  - API health
  - Redis health
- Prometheus metrics endpoint
- API request count and latency metrics
- Order count metrics by source, status, and symbol
- Order lifecycle event metrics
- Redis health gauge

## Planned Features

- Grafana dashboard
- Kubernetes deployment
- AWS deployment
- GitHub Actions CI/CD
- Automated tests
- Alembic database migrations
- Background worker for asynchronous order event processing

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Redis
- Docker
- Docker Compose
- Prometheus
- Uvicorn

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API health |
| GET | `/redis/health` | Check Redis connectivity |
| GET | `/market-data` | View all simulated market data |
| GET | `/market-data/{symbol}` | View market data for one symbol |
| POST | `/orders` | Create a new order |
| GET | `/orders` | Retrieve all orders |
| GET | `/orders/{order_id}` | Retrieve a specific order |
| GET | `/orders/{order_id}/events` | Retrieve lifecycle events for an order |
| POST | `/simulate/order` | Generate a simulated trading order |
| GET | `/queue/order-events` | View recent Redis queued order events |
| GET | `/metrics` | Prometheus metrics endpoint |

## Order Status Logic

TradePulse uses a simplified matching/status engine.

Example market data:

```text
AAPL bid = 184.90
AAPL ask = 185.10
