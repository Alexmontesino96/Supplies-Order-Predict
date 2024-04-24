from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from db.db import Base
from sqlalchemy.orm import relationship


class OrderModel(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    user_id = Column(String,nullable=False)
    # La relación con OrderItem que permite que una orden contenga múltiples productos
    order_items = relationship('OrderItemModel', back_populates='order')

