from pydantic import BaseModel, Field, validator


class Order_Items_Schema(BaseModel):
    order_id: int
    product_id: str
    quantity: int
    price_per_unit: float
    total: float

    @validator("order_id")
    def validate_order_id(cls, value):
        if value > 0:
            return value
        raise ValueError("Order ID must be greater than 0")

    @validator("product_id")
    def validate_product_id(cls, value):
        if len(value) > 0:
            return value
        raise ValueError("Product ID must be greater than 0")

    @validator("quantity")
    def validate_quantity(cls, value):
        if value > 0:
            return value
        raise ValueError("Quantity must be greater than 0")