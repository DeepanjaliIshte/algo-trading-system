import logging
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.strategy import Strategy
from app.models.order import Order
from app.models.trade import Trade
from app.schemas.strategy import (
    StrategyCreate,
    StrategyResponse,
    StrategyStatusResponse,
)
from app.schemas.order import OrderResponse
from app.schemas.trade import TradeResponse
from app.services.auth import get_current_user
from app.services.execution import simulate_strategy_execution

logger = logging.getLogger(__name__)

# ✅ FIXED: Router must have prefix
router = APIRouter(
    prefix="/strategies",
    tags=["Strategies"]
)


# ================================
# Create Strategy
# ================================
@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
def create_strategy(
    payload: StrategyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = Strategy(
        user_id=current_user.id,
        name=payload.name,
        symbol=payload.symbol,
        timeframe=payload.timeframe,
        risk_percentage=payload.risk_percentage,
    )

    db.add(strategy)
    db.commit()
    db.refresh(strategy)

    logger.info(f"Strategy created: {strategy.name} by {current_user.email}")
    return strategy


# ================================
# List Strategies
# ================================
@router.get("/", response_model=List[StrategyResponse])
def list_strategies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Strategy)
        .filter(Strategy.user_id == current_user.id)
        .order_by(Strategy.created_at.desc())
        .all()
    )


# ================================
# Deploy Strategy
# ================================
@router.post("/{strategy_id}/deploy", response_model=StrategyStatusResponse)
def deploy_strategy(
    strategy_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = (
        db.query(Strategy)
        .filter(Strategy.id == strategy_id, Strategy.user_id == current_user.id)
        .first()
    )

    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    if strategy.status == "running":
        raise HTTPException(status_code=400, detail="Strategy already running")

    strategy.status = "running"
    db.commit()

    # Launch background simulation
    background_tasks.add_task(simulate_strategy_execution, strategy_id)

    logger.info(f"Strategy deployed: {strategy.name}")

    return StrategyStatusResponse(
        id=strategy_id,
        status="running",
        message="Strategy deployed successfully",
    )


# ================================
# Stop Strategy
# ================================
@router.post("/{strategy_id}/stop", response_model=StrategyStatusResponse)
def stop_strategy(
    strategy_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = (
        db.query(Strategy)
        .filter(Strategy.id == strategy_id, Strategy.user_id == current_user.id)
        .first()
    )

    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    if strategy.status != "running":
        raise HTTPException(status_code=400, detail="Strategy is not running")

    strategy.status = "stopped"
    db.commit()

    logger.info(f"Strategy stopped: {strategy.name}")

    return StrategyStatusResponse(
        id=strategy_id,
        status="stopped",
        message="Strategy stopped successfully",
    )


# ================================
# List Orders
# ================================
@router.get("/{strategy_id}/orders", response_model=List[OrderResponse])
def list_orders(
    strategy_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = (
        db.query(Strategy)
        .filter(Strategy.id == strategy_id, Strategy.user_id == current_user.id)
        .first()
    )

    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    return (
        db.query(Order)
        .filter(Order.strategy_id == strategy_id)
        .order_by(Order.created_at.desc())
        .all()
    )


# ================================
# List Trades
# ================================
@router.get("/{strategy_id}/trades", response_model=List[TradeResponse])
def list_trades(
    strategy_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = (
        db.query(Strategy)
        .filter(Strategy.id == strategy_id, Strategy.user_id == current_user.id)
        .first()
    )

    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    return (
        db.query(Trade)
        .filter(Trade.strategy_id == strategy_id)
        .order_by(Trade.created_at.desc())
        .all()
    )
