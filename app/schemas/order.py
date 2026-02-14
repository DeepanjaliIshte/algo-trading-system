from pydantic import BaseModel
from datetime import datetime


class OrderResponse(BaseModel):
    id: str
    strategy_id: str
    side: str
    quantity: float
    price: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
