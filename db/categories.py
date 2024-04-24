from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship  # Import the relationship class
from db.db import Base

class Categories_Model(Base):
    __tablename__ = 'department'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    products = relationship('Product_Model', back_populates='category')