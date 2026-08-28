import os
import pytest
from unittest.mock import MagicMock

# Force DATABASE_URL to sqlite in-memory for testing before importing database models
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app import redis_client as redis_client_module
from app.database import Base, get_db
from app.main import app

# Create engine with StaticPool to keep the in-memory SQLite database alive across multiple connections
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create all tables in sqlite testing database
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provides a transactional database session for a single test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def mock_redis():
    """Autouse fixture to mock Redis connection to prevent network calls during testing."""
    mock = MagicMock()
    mock.ping.return_value = True
    mock.xadd.return_value = "1710000000000-0"
    mock.xrevrange.return_value = [
        ("1710000000000-0", {
            "event_id": "evt-123",
            "order_id": "ord-123",
            "event_type": "ORDER_RECEIVED",
            "message": "Mock message",
            "order_status": "ACKED",
            "symbol": "AAPL",
            "side": "BUY",
            "quantity": "100",
            "price": "185.1",
            "trader": "demo",
            "created_at": "2026-06-26T20:00:00Z"
        })
    ]

    # Temporarily patch the actual Redis client instance in redis_client module and event_publisher
    original_client = redis_client_module.redis_client
    redis_client_module.redis_client = mock

    import app.event_publisher
    original_pub_client = app.event_publisher.redis_client
    app.event_publisher.redis_client = mock

    yield mock

    redis_client_module.redis_client = original_client
    app.event_publisher.redis_client = original_pub_client


@pytest.fixture
def client(db_session):
    """Provides a TestClient for making HTTP requests to the FastAPI application with dependency overrides."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
