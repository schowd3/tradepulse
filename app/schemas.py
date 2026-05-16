from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OrderCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    side: Literal["BUY", "SELL"]
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    trader: str = Field(..., min_length=1, max_length=50)


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    symbol: str
    side: str
    quantity: int
    price: float
    trader: str
    status: str
    created_at: datetime


class OrderEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    order_id: str
    event_type: str
    message: str
    created_at: datetime