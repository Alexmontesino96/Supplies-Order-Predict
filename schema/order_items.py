from pydantic import BaseModel, Field, validator
from schema.product import Product_Out_Schema


class Order_Items_Schema(BaseModel):
    order_id: int
    product_id: str
    quantity: int
    price_per_unit: float
    total: float

class Order_Items_Schema_db(BaseModel):
    order_id: int
    product_id: Product_Out_Schema  
    quantity: int
    price_per_unit: float
    total: float

