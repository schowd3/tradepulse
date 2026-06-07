# TradePulse

TradePulse is a production-style trading support and monitoring application built to simulate order flow, expose support APIs, and demonstrate cloud-native deployment practices.

The project models a simplified trading support workflow where orders are created, evaluated against simulated market data, persisted to PostgreSQL, published to Redis as lifecycle events, and monitored through Prometheus and Grafana.

This project is designed to show practical production engineering concepts used in trading systems, including API health checks, order lifecycle tracking, event queues, observability, containerization, Kubernetes deployment, and CI/CD.

---

## What TradePulse Demonstrates

TradePulse is not a real trading system. It is a portfolio project that simulates the types of workflows production support, SRE, DevOps, and backend engineers may support in financial technology environments.

It demonstrates:

- FastAPI-based backend development
- Trading/order workflow simulation
- PostgreSQL persistence
- Redis Streams for event queueing
- Prometheus metrics
- Grafana dashboards
- Docker Compose local orchestration
- Kubernetes manifests
- Kubernetes liveness and readiness probes
- Kubernetes CPU and memory requests/limits
- GitHub Actions CI
- Docker image publishing to Amazon ECR

---

## Current Features

### API and Trading Workflow

- FastAPI backend
- Swagger API documentation
- Order creation API
- Simulated trade/order event generator
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

### Persistence and Event Queue

- PostgreSQL database persistence
- SQLAlchemy ORM models
- Redis Streams event queue
- API endpoint for recent queued order events

### Observability

- Health check endpoints
  - API health
  - Redis health
- Prometheus metrics endpoint
- API request count and latency metrics
- Order count metrics by source, status, and symbol
- Order lifecycle event metrics
- Redis health gauge
- Grafana dashboard
- Provisioned Prometheus datasource
- Provisioned TradePulse monitoring dashboard

### Docker and Kubernetes

- Dockerfile for the FastAPI application
- Docker Compose stack for local development
- Kubernetes deployment manifests for:
  - API
  - PostgreSQL
  - Redis
  - Prometheus
  - Grafana
- Kubernetes Namespace, ConfigMap, Secret, Service, Deployment, and PersistentVolumeClaim configuration
- Kubernetes liveness and readiness probes
- Kubernetes CPU and memory requests/limits

### CI/CD and AWS Image Publishing

- GitHub Actions CI workflow
- Python dependency installation and source compilation
- Docker image build validation
- Kubernetes manifest validation with kubeconform
- Automated Docker image push to Amazon ECR using GitHub Actions and AWS OIDC

---

## Tech Stack

- Python
- FastAPI
- Uvicorn
- PostgreSQL
- SQLAlchemy
- Redis
- Prometheus
- Grafana
- Docker
- Docker Compose
- Kubernetes
- GitHub Actions
- AWS ECR
- AWS IAM OIDC

---

## Project Architecture

```text
Client / Swagger UI
        |
        v
FastAPI TradePulse API
        |
        |--- PostgreSQL
        |       Stores orders and lifecycle events
        |
        |--- Redis Streams
        |       Publishes order lifecycle events
        |
        |--- Prometheus /metrics
                Exposes application metrics
                    |
                    v
                Grafana Dashboard
```

---

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

---

## Order Status Logic

TradePulse uses a simplified order status engine based on simulated market data.

Example market data:

```text
AAPL bid = 184.90
AAPL ask = 185.10
```

Example rules:

```text
BUY order:
- If order price >= ask price, the order is FILLED
- Otherwise, the order is ACKED

SELL order:
- If order price <= bid price, the order is FILLED
- Otherwise, the order is ACKED

Unsupported symbol:
- Order is REJECTED
```

---

## Running Locally with Docker Compose

Docker Compose is the easiest way to run the full TradePulse stack locally.

### Prerequisites

Install:

- Docker Desktop
- Git

### Clone the Repository

```bash
git clone https://github.com/schowd3/tradepulse.git
cd tradepulse
```

### Start the Full Local Stack

```bash
docker compose up -d --build
```

This starts:

- TradePulse API
- PostgreSQL
- Redis
- Prometheus
- Grafana

### Check Running Containers

```bash
docker ps
```

Expected services include:

```text
tradepulse-api
tradepulse-postgres
tradepulse-redis
tradepulse-prometheus
tradepulse-grafana
```

### Open the API Documentation

Open Swagger UI:

```text
http://localhost:8000/docs
```

---

## Local Service URLs

| Service | URL |
|---|---|
| FastAPI Swagger UI | `http://localhost:8000/docs` |
| FastAPI health check | `http://localhost:8000/health` |
| Redis health check | `http://localhost:8000/redis/health` |
| Prometheus | `http://localhost:9090` |
| Grafana | `http://localhost:3000` |

Grafana login:

```text
Username: admin
Password: admin
```

---

## Testing the API Locally

### Check API Health

```bash
curl http://localhost:8000/health
```

PowerShell:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

### Check Redis Health

```bash
curl http://localhost:8000/redis/health
```

PowerShell:

```powershell
Invoke-RestMethod http://localhost:8000/redis/health
```

### View Simulated Market Data

```bash
curl http://localhost:8000/market-data
```

PowerShell:

```powershell
Invoke-RestMethod http://localhost:8000/market-data
```

### Create an Order

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "side": "BUY",
    "quantity": 100,
    "price": 185.10,
    "trader": "demo-trader"
  }'
```

PowerShell:

```powershell
$body = @{
    symbol = "AAPL"
    side = "BUY"
    quantity = 100
    price = 185.10
    trader = "demo-trader"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://localhost:8000/orders -ContentType "application/json" -Body $body
```

### Generate a Simulated Order

```bash
curl -X POST http://localhost:8000/simulate/order
```

PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/simulate/order
```

### View All Orders

```bash
curl http://localhost:8000/orders
```

PowerShell:

```powershell
Invoke-RestMethod http://localhost:8000/orders
```

### View Recent Redis Queued Order Events

```bash
curl http://localhost:8000/queue/order-events
```

PowerShell:

```powershell
Invoke-RestMethod http://localhost:8000/queue/order-events
```

### View Prometheus Metrics

```bash
curl http://localhost:8000/metrics
```

PowerShell:

```powershell
Invoke-RestMethod http://localhost:8000/metrics
```

---

## Prometheus Metrics

Prometheus scrapes TradePulse metrics from:

```text
http://tradepulse-api:8000/metrics
```

From the host machine, the same metrics are available at:

```text
http://localhost:8000/metrics
```

Useful Prometheus queries:

```promql
tradepulse_http_requests_total
```

```promql
tradepulse_orders_created_total
```

```promql
tradepulse_order_events_created_total
```

```promql
tradepulse_redis_up
```

```promql
histogram_quantile(0.95, sum(rate(tradepulse_http_request_duration_seconds_bucket[5m])) by (le, endpoint))
```

---

## Grafana Dashboard

Grafana is provisioned automatically through Docker Compose.

Open:

```text
http://localhost:3000
```

Login with:

```text
admin / admin
```

Then go to:

```text
Dashboards → TradePulse → TradePulse Production Monitoring
```

The dashboard includes panels for:

- Total orders created
- Redis health
- API request rate
- Orders by status
- Orders by source
- P95 API latency
- Order lifecycle events

---

## Stopping the Local Stack

To stop the containers:

```bash
docker compose down
```

To stop the containers and remove local volumes:

```bash
docker compose down -v
```

Use `-v` only when you want to clear the local PostgreSQL and Redis data.

---

## Running Locally with Kubernetes

The repository also includes Kubernetes manifests for running TradePulse locally with Docker Desktop Kubernetes.

Docker Compose is recommended for the simplest local setup. Kubernetes is optional and useful for demonstrating deployment, probes, resource limits, and service orchestration.

### Prerequisites

Install and enable:

- Docker Desktop
- Kubernetes in Docker Desktop
- kubectl

Verify Kubernetes is running:

```bash
kubectl get nodes
```

### Build the Local API Image

```bash
docker build -t tradepulse-api:latest .
```

### Apply Kubernetes Manifests

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/prometheus-configmap.yaml
kubectl apply -f k8s/prometheus.yaml
kubectl apply -f k8s/grafana-datasource-configmap.yaml
kubectl apply -f k8s/grafana-dashboard-provider-configmap.yaml
kubectl apply -f k8s/grafana-dashboard-configmap.yaml
kubectl apply -f k8s/grafana.yaml
```

### Check Kubernetes Pods

```bash
kubectl get pods -n tradepulse
```

Expected pods include:

```text
tradepulse-api
tradepulse-postgres
tradepulse-redis
tradepulse-prometheus
tradepulse-grafana
```

### Access the API

```bash
kubectl port-forward svc/tradepulse-api 8080:8000 -n tradepulse
```

Open:

```text
http://localhost:8080/docs
```

### Access Prometheus

```bash
kubectl port-forward svc/tradepulse-prometheus 9091:9090 -n tradepulse
```

Open:

```text
http://localhost:9091
```

### Access Grafana

```bash
kubectl port-forward svc/tradepulse-grafana 3001:3000 -n tradepulse
```

Open:

```text
http://localhost:3001
```

Login:

```text
admin / admin
```

---

## GitHub Actions CI/CD

The repository includes a GitHub Actions workflow that runs on pushes and pull requests to `main`.

The workflow:

- Checks out the repository
- Sets up Python
- Installs dependencies
- Compiles Python source
- Builds the Docker image
- Validates Kubernetes manifests with kubeconform
- Pushes the Docker image to Amazon ECR on main branch updates

AWS deployment is optional. TradePulse can be fully run locally without AWS.

---

## AWS Status

AWS exploration is currently paused.

Completed AWS-related work:

- Amazon ECR repository support
- GitHub Actions OIDC authentication
- Automated Docker image push to ECR

AWS is not required to run TradePulse locally. The full local stack can be run with Docker Compose.

Future AWS work may include:

- ECS Fargate deployment
- RDS PostgreSQL
- ElastiCache Redis
- Terraform infrastructure as code

---

## Common Troubleshooting

### API Is Not Reachable on Port 8000

Check containers:

```bash
docker ps
```

Check API logs:

```bash
docker compose logs --tail=100 api
```

Restart the stack:

```bash
docker compose down
docker compose up -d --build
```

### Docker Compose Build Fails

Rebuild without cache:

```bash
docker compose build --no-cache
docker compose up -d
```

### Kubernetes Port-Forward Says the Port Is Already in Use

Use a different local port:

```bash
kubectl port-forward svc/tradepulse-api 8081:8000 -n tradepulse
```

Or stop existing kubectl port-forward processes.

PowerShell:

```powershell
Get-Process kubectl
Stop-Process -Name kubectl -Force
```

### Kubernetes API Image Does Not Start Locally

Make sure the image exists locally:

```bash
docker build -t tradepulse-api:latest .
docker images
```

Then restart the deployment:

```bash
kubectl rollout restart deployment/tradepulse-api -n tradepulse
```

### Python Cache Files Appear in Git Status

Do not commit `__pycache__` or `.pyc` files.

```bash
git restore app/__pycache__/main.cpython-312.pyc
```

---

## Planned Improvements

- Automated tests
- Alembic database migrations
- Background worker for asynchronous order event processing
- ECS Fargate deployment
- RDS PostgreSQL
- ElastiCache Redis
- Terraform infrastructure as code

---

## Project Purpose

TradePulse was built as a hands-on portfolio project to demonstrate backend engineering, production support, observability, containerization, Kubernetes, CI/CD, and cloud-readiness in a trading systems context.

The project is intended to be understandable, runnable locally, and useful as a foundation for discussing production engineering workflows in fintech environments.