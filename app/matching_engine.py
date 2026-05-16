from app.market_data import get_market_data


def determine_order_status(symbol: str, side: str, price: float) -> str:
    market_data = get_market_data(symbol)

    if market_data is None:
        return "REJECTED"

    side = side.upper()

    if side == "BUY":
        if price >= market_data.ask:
            return "FILLED"
        return "ACKED"

    if side == "SELL":
        if price <= market_data.bid:
            return "FILLED"
        return "ACKED"

    return "REJECTED"