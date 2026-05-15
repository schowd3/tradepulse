from pydantic import BaseModel, Field
from typing import Literal


class OrderCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    side: Literal["BUY", "SELL"]
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    trader: str = Field(..., min_length=1, max_length=50)


class OrderResponse(BaseModel):
    order_id: str
    symbol: str
    side: str
    quantity: int
    price: float
    trader: str
    status: str
    created_at: str