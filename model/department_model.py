from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship  # Import the relationship class
from db.db import Base

class Department_Model(Base):
    __tablename__ = 'department'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    products = relationship('Product', back_populates='department')
