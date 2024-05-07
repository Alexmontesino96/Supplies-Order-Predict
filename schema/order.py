from pydantic import BaseModel, Field, validator
import csv
from pydantic import computed_field
from typing import Optional
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv
import os
import json
from schema.order_items import Order_Items_Schema_db
from db.db import Session
from model.order_item_model import OrderItemModel
from model.order_model import OrderModel

load_dotenv()
STATUS = json.loads(os.getenv('STATUS'))

class Status_Order(Enum):
    PENDING = STATUS[0]
    IN_PROGRESS = STATUS[1]
    COMPLETED = STATUS[2]


class Order_Schema(BaseModel):
    id : int = Field(None, alias='id')
    date: datetime
    user_id: str
    status: Status_Order = Field(default=Status_Order.IN_PROGRESS)

class Order_Schema_Total(BaseModel):
    id : int = Field(None, alias='id')
    date: datetime
    user_id: str
    status: Status_Order = Field(default=Status_Order.IN_PROGRESS)
    total: float = Field(default=0.0, computed_field=True)
    total_items: int = Field(default=0, computed_field=True)

    @property
    def calculate_total_and_total_items(self) -> float:
        """
        Calcula el total sumando los totales de cada ítem asociado a la orden.
        """
        with Session() as db:
            order_items = db.query(OrderItemModel).filter(OrderItemModel.order_id == self.id).all()
            total = sum(item.total for item in order_items)
            total_items = len(order_items)
        return total, total_items

    def __init__(self, **kwargs):
        """
        Calcula el total cuando se crea la instancia.
        """
        super().__init__(**kwargs)
        self.total, self.total_items = self.calculate_total_and_total_items

    @staticmethod
    def serialize_order_db(order: OrderModel):
            
        order_with_total = Order_Schema_Total(
            id=order.id,
            date=order.date,
            user_id=order.user_id,
        )
        return order_with_total

class Order_Schema_Out(BaseModel):
    order: Order_Schema_Total
    order_items: list[Order_Items_Schema_db]

    model_config = {
        'from_attributes': True
    }