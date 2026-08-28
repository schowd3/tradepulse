from datetime import datetime
from fastapi import APIRouter
from app.redis_client import check_redis_connection
from app.metrics import REDIS_UP

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    return {
        "status": "UP",
        "service": "tradepulse-api",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/redis/health")
def redis_health_check() -> dict:
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
