from pydantic import BaseModel, Field, validator
from schema.product import Product_Out_Schema
import csv
from pydantic import computed_field
from typing import Optional
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv
import os
import json
from schema.order_items import Order_Items_Schema_db

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

class Order_Schema_Out(BaseModel):
    order: Order_Schema
    order_items: list[Order_Items_Schema_db]
    total: Optional[float] = Field(default=0.0)

    model_config = {
        'from_attributes': True
    }


