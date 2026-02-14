import asyncio
import random
import logging
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.strategy import Strategy
from app.models.order import Order
from app.models.trade import Trade

logger = logging.getLogger(__name__)


async def simulate_strategy_execution(strategy_id: str) -> None:
    """
    Simulates one full trading cycle:
    1. Wait for entry signal
    2. Place buy order
    3. Wait for exit signal
    4. Place sell order
    5. Record trade
    6. Update strategy status
    """

    logger.info(f"Starting execution simulation for strategy {strategy_id}")

    db: Session = SessionLocal()

    try:
        # ----------------------------
        # Simulate Entry Delay
        # ----------------------------
        await asyncio.sleep(random.uniform(2, 5))

        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()

        if not strategy or strategy.status != "running":
            logger.info(f"Strategy {strategy_id} no longer running, aborting.")
            return

        # ----------------------------
        # Simulate Entry Order
        # ----------------------------
        entry_price = round(random.uniform(100, 500), 2)
        quantity = round(random.uniform(0.1, 10), 4)

        buy_order = Order(
            strategy_id=strategy_id,
            side="buy",
            quantity=quantity,
            price=entry_price,
            status="filled",
        )

        db.add(buy_order)
        db.commit()

        logger.info(f"Buy order filled: {quantity} @ {entry_price}")

        # ----------------------------
        # Simulate Exit Delay
        # ----------------------------
        await asyncio.sleep(random.uniform(3, 8))

        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()

        if not strategy or strategy.status != "running":
            logger.info(f"Strategy {strategy_id} stopped during execution.")
            return

        # ----------------------------
        # Simulate Exit Order
        # ----------------------------
        price_change = random.uniform(-0.05, 0.08)
        exit_price = round(entry_price * (1 + price_change), 2)

        sell_order = Order(
            strategy_id=strategy_id,
            side="sell",
            quantity=quantity,
            price=exit_price,
            status="filled",
        )

        db.add(sell_order)

        pnl = round((exit_price - entry_price) * quantity, 2)

        trade = Trade(
            strategy_id=strategy_id,
            entry_price=entry_price,
            exit_price=exit_price,
            pnl=pnl,
            mode="paper",
        )

        db.add(trade)

        # Mark strategy inactive after cycle
        strategy.status = "inactive"

        db.commit()

        logger.info(
            f"Trade completed for strategy {strategy_id}: "
            f"entry={entry_price}, exit={exit_price}, pnl={pnl}"
        )

    except Exception as e:
        logger.error(f"Execution error for strategy {strategy_id}: {e}")
        db.rollback()

    finally:
        db.close()
