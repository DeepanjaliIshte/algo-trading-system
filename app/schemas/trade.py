from pydantic import BaseModel
from datetime import datetime


class TradeResponse(BaseModel):
    id: str
    strategy_id: str
    entry_price: float
    exit_price: float
    pnl: float
    mode: str
    created_at: datetime

    class Config:
        from_attributes = True
