import csv
from schema.product import Product_Out_Schema, Product_In_Schema
from schema.order import Order_Schema
from schema.order_items import Order_Items_Schema
from datetime import datetime
from model.order_model import OrderModel
from db.db import Session
from fastapi import UploadFile, File
from io import StringIO
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from model.order_item_model import OrderItemModel
from model.product_model import Product as ProductModel
import re

class Order_Service():
    def __init__(self, db_session):
        self.db_session = db_session

    def add_product_to_order(self, product_id: int, order_id: int, quantity: int):
        with self.db_session() as db:
            product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
            order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
            if product is None or order is None:
                return JSONResponse(content={"message": "Product or Order not found"}, status_code=404)
            
            order_item = OrderItemModel(
                order_id=order_id,
                product_id=product_id,
                quantity=quantity,
                price_per_unit=product.price,
                total=quantity * product.price
            )
            db.add(order_item)
            db.commit()
            return JSONResponse(content={"message": "Product added to order successfully"}, status_code=201)
    def delete_items_from_order(self, product_id: int, order_id: int):
        with self.db_session() as db:
        
            order_item = db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).all()

            if order_item is None:
                return JSONResponse(content={"message": "Order not found"}, status_code=404)
            
            for item in order_item:
                if item.product_id == product_id:
                    db.delete(item)
            db.commit()
            return JSONResponse(content={"message": "Order items deleted successfully"}, status_code=200)
        
    def delete_order(self, order_id: int):
        with self.db_session() as db:
            order = db.query(OrderModel).filter(OrderModel.id == order_id).first()

            if order is None:
                return JSONResponse(content={"message": "Order not found"}, status_code=404)
            
            db.delete(order)
            db.commit()
            return JSONResponse(content={"message": "Order deleted successfully"}, status_code=200)
        
    def search_order_by_user(self, user_id: int):
        with self.db_session() as db:
            orders = db.query(OrderModel).filter(OrderModel.user_id == user_id).all()
            if orders is None:
                return JSONResponse(content={"message": "Order not found"}, status_code=404)
            return JSONResponse(content=[order.id for order in orders], status_code=200)

    def search_order_by_id(self, order_id: int):
        with self.db_session() as db:

            list_product_related = []
            order = db.query(OrderModel).filter(OrderModel.id == order_id).first()

            if order is None:
                return JSONResponse(content={"message": "Order not found"}, status_code=404)
            
            order_items = db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).all()
            
            for order in order_items:
                product_realted_with_order = order.product
                list_product_related.append(product_realted_with_order)

            return list_product_related
        
    def search_product_in_all_orders(self, product_id: int):
        with self.db_session() as db:
            orders = db.query(OrderItemModel).filter(OrderItemModel.product_id == product_id).all()
            if orders is None:
                return JSONResponse(content={"message": "Product not found in any order"}, status_code=404)
            return JSONResponse(content=[order.order_id for order in orders], status_code=200)

    def process_order_csv(self, user_id: int, csv_file: UploadFile = File(...)):
        if not csv_file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Invalid file type, only CSV files are accepted.")

        order = self.create_order(user_id)
        if order is None:
            raise HTTPException(status_code=500, detail="Failed to create order.")

        content = StringIO(csv_file.file.read().decode('utf-8'))
        reader = csv.DictReader(content)

        with Session() as db:
            for row in reader:
                if 'Quantity' in row:
                    quantity = int(row['Quantity'])
                else:
                    quantity = row["QTY"]
                
                if 'Price' in row:
                    price = float(re.sub(r'[^\d.]', '', row['Price']))
                else:
                    price = row["Price per Case"]
                if 'Distribution #' in row:
                    product_id = str(row['Distribution #'])
                else:
                    product_id = row["Customer #"]
                if 'Subtotal' in row:
                    subtotal = float(row['Subtotal'])
                else:
                    subtotal = price * quantity

                try:
                    order_item = Order_Items_Schema(
                        order_id=order.id,
                        product_id=product_id,
                        quantity=quantity,
                        price_per_unit=price,
                        total=subtotal
                    )
                except ValueError as e:
                    print(f"An error occurred while processing order items: {e}")
                    continue
                order_item_model = OrderItemModel(**order_item.model_dump())
                db.add(order_item_model)
                db.commit()
            return (201, order.id)
        
    def create_order(self,user_id: int):
        try:
            with self.db_session() as db:
                new_order = Order_Schema(date=datetime.now(), user_id=user_id)
                new_order_model = OrderModel(**new_order.model_dump())
                db.add(new_order_model)
                db.commit()
                db.refresh(new_order_model)  # Obtener el ID generado
                print(new_order)
                return new_order_model
        except Exception as e:
            print(f"An error occurred while creating order: {e}")
            return None
        
    def get_all_order(self):
        with self.db_session() as db:
            orders = db.query(OrderModel).all()
            if orders is None:
                return JSONResponse(content={"message": "Not order in database"}, status_code=404)
            return JSONResponse(content=[order.id for order in orders], status_code=200)
