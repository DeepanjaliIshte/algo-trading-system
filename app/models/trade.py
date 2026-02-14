import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_id = Column(String, ForeignKey("strategies.id"), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=False)
    pnl = Column(Float, nullable=False)
    mode = Column(String, default="paper")  # paper | live
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    strategy = relationship("Strategy", back_populates="trades")
