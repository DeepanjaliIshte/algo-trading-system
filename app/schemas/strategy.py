from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class StrategyCreate(BaseModel):
    name: str
    symbol: str
    timeframe: str
    risk_percentage: float = 1.0


class StrategyResponse(BaseModel):
    id: str
    user_id: str
    name: str
    symbol: str
    timeframe: str
    risk_percentage: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class StrategyStatusResponse(BaseModel):
    id: str
    status: str
    message: str
