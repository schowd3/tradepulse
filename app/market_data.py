from dataclasses import dataclass
from random import uniform


@dataclass
class MarketData:
    symbol: str
    bid: float
    ask: float


BASE_MARKET_DATA = {
    "AAPL": {"bid": 184.90, "ask": 185.10},
    "MSFT": {"bid": 420.25, "ask": 420.55},
    "TSLA": {"bid": 175.10, "ask": 175.45},
    "NVDA": {"bid": 910.20, "ask": 911.00},
    "UST10Y": {"bid": 99.75, "ask": 99.80},
    "EURUSD": {"bid": 1.0831, "ask": 1.0834},
    "BTCUSD": {"bid": 67250.00, "ask": 67275.00},
}


def get_market_data(symbol: str) -> MarketData | None:
    symbol = symbol.upper()

    if symbol not in BASE_MARKET_DATA:
        return None

    base = BASE_MARKET_DATA[symbol]

    # Small random movement to simulate live market changes
    bid_shift = uniform(-0.05, 0.05)
    ask_shift = uniform(-0.05, 0.05)

    bid = round(base["bid"] + bid_shift, 4)
    ask = round(base["ask"] + ask_shift, 4)

    # Safety: make sure bid is always less than ask
    if bid >= ask:
        ask = bid + 0.01

    return MarketData(symbol=symbol, bid=bid, ask=ask)


def get_all_market_data():
    return {
        symbol: get_market_data(symbol)
        for symbol in BASE_MARKET_DATA.keys()
    }