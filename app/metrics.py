import time
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
from fastapi import Request

# Core API & HTTP metrics
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

# Business-specific metrics
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

REDIS_UP = Gauge(
    "tradepulse_redis_up",
    "Redis health status. 1 means up, 0 means down."
)


def normalize_path(path: str) -> str:
    if path.startswith("/orders/") and path.endswith("/events"):
        return "/orders/{order_id}/events"

    if path.startswith("/orders/"):
        return "/orders/{order_id}"

    return path


async def collect_http_metrics(request: Request, call_next):
    # Skip metrics logging for /metrics and /health endpoint to avoid spamming logs
    path = request.url.path
    if path in ("/metrics", "/health", "/redis/health"):
        return await call_next(request)

    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time
    endpoint = normalize_path(path)

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


# Create ASGI app for metrics endpoint
metrics_app = make_asgi_app()
