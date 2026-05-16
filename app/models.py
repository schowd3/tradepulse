from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(4), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    trader = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="NEW")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class OrderEvent(Base):
    __tablename__ = "order_events"

    event_id = Column(String, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    message = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)