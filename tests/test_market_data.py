from app.market_data import get_market_data, get_all_market_data, MarketData


def test_get_market_data_valid():
    data = get_market_data("AAPL")
    assert isinstance(data, MarketData)
    assert data.symbol == "AAPL"
    assert isinstance(data.bid, float)
    assert isinstance(data.ask, float)
    assert data.bid < data.ask


def test_get_market_data_invalid():
    data = get_market_data("INVALID_SYM")
    assert data is None


def test_get_market_data_case_insensitive():
    data = get_market_data("aapl")
    assert data is not None
    assert data.symbol == "AAPL"


def test_get_all_market_data():
    all_data = get_all_market_data()
    assert isinstance(all_data, dict)
    assert "AAPL" in all_data
    assert "MSFT" in all_data
    assert isinstance(all_data["AAPL"], MarketData)
