from pydantic import BaseModel, Field, model_validator, validator
from schema.product import Product_Out_Schema
from db.db import session_scope
from model.order_model import OrderModel
from model.product_model import Product



class Order_Items_Schema(BaseModel):
    
    order_id: int
    product_id: str
    quantity: int
    price_per_unit: float
    total: float

    @validator("total")
    def validate_total(cls, total):
        if total < 0:
            raise ValueError("Total must be greater than 0")
        if not total or total != cls.quantity * cls.price_per_unit:
            total = cls.quantity * cls.price_per_unit
        return total

    @validator("order_id", "product_id")
    def check_order_and_product(cls, values):
        order_id = values.get('order_id')
        product_id = values.get('product_id')
        with session_scope() as session:
            order = session.query(OrderModel).filter(OrderModel.id == order_id).first()
            if not order:
                raise ValueError("Order not found")

            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise ValueError("Product not found")

        return values
    

        

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

