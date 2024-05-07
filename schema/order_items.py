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
    product: Product_Out_Schema  
    quantity: int
    price_per_unit: float
    total: float

    @classmethod
    def serialize_order_item_db(cls, order_item):
        return cls(
            order_id=order_item.order_id,
            product=Product_Out_Schema.serialize_product_db(order_item.product),
            quantity=order_item.quantity,
            price_per_unit=order_item.price_per_unit,
            total=order_item.total
        )

