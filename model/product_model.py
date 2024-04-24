from db.db import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean,DateTime
from sqlalchemy.orm import relationship


class Product(Base):
    __tablename__ = 'products'

    id = Column(String, primary_key=True)
    name = Column(String(50))
    price = Column(Float)
    pack = Column(String(50))
    uom = Column(String(50))
    comments = Column(String(250))
    week_average_last_30_days = Column(Float)
    active = Column(Boolean)
    date_active = Column(DateTime)
    date_deactive = Column(DateTime or None)
    department_name = Column(String, ForeignKey('department.name'))
    priority = Column(Integer)
    department = relationship('Department_Model', back_populates='products')
    order_items = relationship('OrderItemModel', back_populates='product')