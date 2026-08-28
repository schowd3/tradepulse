from fastapi import APIRouter, HTTPException
from app.market_data import get_all_market_data, get_market_data

router = APIRouter()


@router.get("/market-data")
def market_data() -> dict:
    return get_all_market_data()


@router.get("/market-data/{symbol}")
def market_data_by_symbol(symbol: str) -> dict:
    data = get_market_data(symbol)

    if data is None:
        raise HTTPException(status_code=404, detail="Market data not found for symbol")

    # Since it's a dataclass, we can return it as-is or serialized
    return {
        "symbol": data.symbol,
        "bid": data.bid,
        "ask": data.ask
    }
