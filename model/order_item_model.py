from sqlalchemy import Column, Integer, Float, ForeignKey
from db.db import Base
from sqlalchemy.orm import relationship


class OrderItemModel(Base):
    __tablename__ = 'order_items'

    order_id = Column(Integer, ForeignKey('orders.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

    # Relaciones para acceder a la orden y al producto desde OrderItem
    order = relationship('OrderModel', back_populates='order_items')
    product = relationship('Product', back_populates='order_items', lazy='joined')
