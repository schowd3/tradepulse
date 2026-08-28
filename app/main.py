import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import Base, engine
from app.metrics import metrics_app, collect_http_metrics
from app.routers import health, market_data, orders

# Ensure database tables are created
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TradePulse",
    description="Trading Support / Production Monitoring API",
    version="0.6.0"
)

# Attach Prometheus HTTP request tracking middleware
app.middleware("http")(collect_http_metrics)

# Mount Prometheus metrics endpoint
app.mount("/metrics", metrics_app)

# Include sub-routers
app.include_router(health.router)
app.include_router(market_data.router)
app.include_router(orders.router)

# Serve the frontend dashboard
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def dashboard():
    """Redirect root to the TradePulse dashboard UI."""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))