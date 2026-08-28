import random
from sqlalchemy.orm import Session
from app.models import Order
from app.market_data import BASE_MARKET_DATA, get_market_data
from app.orders_service import create_and_publish_order


def simulate_random_order(db: Session) -> Order:
    symbols = list(BASE_MARKET_DATA.keys())
    sides = ["BUY", "SELL"]
    traders = ["trader_nyc_01", "trader_ldn_02", "trader_tokyo_03"]

    symbol = random.choice(symbols)
    side = random.choice(sides)
    market = get_market_data(symbol)

    if market is None:
        # Fallback in case market data is completely empty/invalid
        price = 100.0
    elif side == "BUY":
        price = round(random.uniform(market.bid, market.ask + 1.0), 4)
    else:
        price = round(random.uniform(market.bid - 1.0, market.ask), 4)

    quantity = random.randint(100, 10000)
    trader = random.choice(traders)

    return create_and_publish_order(
        db=db,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        trader=trader,
        source="simulator"
    )
