from pydantic import BaseModel, Field, validator
from schema.product import Product_Out_Schema
import csv
from pydantic import computed_field
from typing import Optional
from datetime import datetime

class Order_Schema(BaseModel):
    id : int = Field(None, alias='id')
    date: datetime
    user_id: str

