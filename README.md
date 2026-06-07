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