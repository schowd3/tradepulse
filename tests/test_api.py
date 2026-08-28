def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["service"] == "tradepulse-api"
    assert "timestamp" in data


def test_redis_health_check_up(client, mock_redis):
    mock_redis.ping.return_value = True
    response = client.get("/redis/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["service"] == "tradepulse-redis"


def test_redis_health_check_down(client, mock_redis):
    # Simulate redis error
    import redis
    mock_redis.ping.side_effect = redis.RedisError("Connection lost")
    response = client.get("/redis/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DOWN"
    assert data["service"] == "tradepulse-redis"


def test_get_all_market_data(client):
    response = client.get("/market-data")
    assert response.status_code == 200
    data = response.json()
    assert "AAPL" in data
    assert "bid" in data["AAPL"]


def test_get_market_data_by_symbol(client):
    response = client.get("/market-data/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert "bid" in data
    assert "ask" in data


def test_get_market_data_not_found(client):
    response = client.get("/market-data/NOT_EXIST")
    assert response.status_code == 404


def test_create_order_manual(client):
    order_payload = {
        "symbol": "AAPL",
        "side": "BUY",
        "quantity": 100,
        "price": 1000.0,  # Will result in FILLED
        "trader": "test-trader"
    }
    response = client.post("/orders", json=order_payload)
    assert response.status_code == 200
    order_data = response.json()
    assert order_data["symbol"] == "AAPL"
    assert order_data["side"] == "BUY"
    assert order_data["quantity"] == 100
    assert order_data["price"] == 1000.0
    assert order_data["trader"] == "test-trader"
    assert order_data["status"] == "FILLED"
    assert "order_id" in order_data
    assert "created_at" in order_data


def test_get_orders(client):
    # Create an order first
    order_payload = {
        "symbol": "MSFT",
        "side": "SELL",
        "quantity": 50,
        "price": 1.0,  # Will result in FILLED
        "trader": "test-trader"
    }
    client.post("/orders", json=order_payload)

    response = client.get("/orders")
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) >= 1
    assert orders[0]["symbol"] == "MSFT"


def test_get_order_by_id(client):
    order_payload = {
        "symbol": "TSLA",
        "side": "BUY",
        "quantity": 200,
        "price": 10.0,
        "trader": "test-trader"
    }
    create_resp = client.post("/orders", json=order_payload)
    order_id = create_resp.json()["order_id"]

    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    order_data = response.json()
    assert order_data["order_id"] == order_id
    assert order_data["symbol"] == "TSLA"


def test_get_order_events(client):
    order_payload = {
        "symbol": "TSLA",
        "side": "BUY",
        "quantity": 200,
        "price": 10.0,
        "trader": "test-trader"
    }
    create_resp = client.post("/orders", json=order_payload)
    order_id = create_resp.json()["order_id"]

    response = client.get(f"/orders/{order_id}/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) >= 1
    assert events[0]["order_id"] == order_id
    # Every order gets at least ORDER_RECEIVED
    assert events[0]["event_type"] == "ORDER_RECEIVED"


def test_simulate_order(client):
    response = client.post("/simulate/order")
    assert response.status_code == 200
    order_data = response.json()
    assert "order_id" in order_data
    assert order_data["quantity"] > 0
    assert order_data["status"] in ("FILLED", "ACKED", "REJECTED")


def test_get_queued_events_from_redis(client):
    response = client.get("/queue/order-events?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["stream"] == "tradepulse:order_events"
    assert data["limit"] == 5
    assert len(data["events"]) == 1
    assert data["events"][0]["symbol"] == "AAPL"
