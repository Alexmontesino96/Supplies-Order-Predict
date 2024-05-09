from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from schema.status_order import Status_Order
from db.db import Base
from sqlalchemy.orm import relationship


class OrderModel(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    user_id = Column(String,nullable=False)
    order_items = relationship('OrderItemModel', back_populates='order')
    status = Column(Enum(Status_Order), nullable=False)

