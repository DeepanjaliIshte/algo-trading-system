import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_id = Column(String, ForeignKey("strategies.id"), nullable=False)
    side = Column(String, nullable=False)  # buy | sell
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending | filled | cancelled
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    strategy = relationship("Strategy", back_populates="orders")
