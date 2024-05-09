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
from fastapi.encoders import jsonable_encoder
from model.order_item_model import OrderItemModel
from schema.order_items import Order_Items_Schema_db
from model.product_model import Product as ProductModel
import re
from sqlalchemy.orm import joinedload
from schema.order import Order_Schema_Out, Order_Schema_Total
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from fastapi import status


class Order_Service():
    def __init__(self, db_session):
        self.db_session = db_session

    def add_product_to_order(self, product_id: str, order_id: int, quantity: int):

        product = self.db_session.query(ProductModel).filter(ProductModel.id == product_id).first()
        order = self.db_session.query(OrderModel).filter(OrderModel.id == order_id).first()
        if product is None or order is None:
            return JSONResponse(content={"message": "Product or Order not found"}, status_code=404)
        try:
            order_item = OrderItemModel(
                order_id=order_id,
                product_id=product_id,
                quantity=quantity,
                price_per_unit=product.price,
                total=quantity * product.price
            )
            self.db_session.add(order_item)
            self.db_session.commit()

        except ValueError as e:
            print(f"An error occurred while adding product to order: {e}")
            return JSONResponse(content={"message": "An error occurred while adding product to order"}, status_code=500)
        try:
            self.db_session.add(order_item)
            self.db_session.commit()
        except SQLAlchemyError as e:
            print(f"An error occurred while adding product to order: {e}")
            return JSONResponse(content={"message": "An error occurred while adding product to order"}, status_code=500)

        return JSONResponse(content={"message": "Product added to order successfully"}, status_code=201)

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
        order = self.db_session.query(OrderModel).filter(OrderModel.id == order_id).options(
            joinedload(OrderModel.order_items).joinedload(OrderItemModel.product)).first()
        if not order:
            return JSONResponse(content={"message": "Order not found"}, status_code=404)

        # Manejo de items con producto no disponible
        order_items = [item for item in order.order_items if item.product is not None]
        if not order_items:
            return JSONResponse(content={"message": "No valid order items found"}, status_code=404)

        new_order_schema_out = Order_Schema_Out(
            order=Order_Schema_Total.serialize_order_db(order),
            order_items=[Order_Items_Schema_db.serialize_order_item_db(item) for item in order_items]
        )

        return new_order_schema_out

    def search_product_in_all_orders(self, product_id: int):
        orders = self.db_session.query(OrderItemModel).filter(OrderItemModel.product_id == product_id).all()
        if orders is None:
            return JSONResponse(content={"message": "Product not found in any order"}, status_code=404)
        return JSONResponse(content=[order.order_id for order in orders], status_code=200)

    def process_order_csv(self, user_email: int, csv_file: UploadFile = File(...))-> JSONResponse:
        if not csv_file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Invalid file type, only CSV files are accepted.")

        order = self.create_order(user_email)
        if order is None:
            raise HTTPException(status_code=500, detail="Failed to create order.")
        try:
            content = StringIO(csv_file.file.read().decode('utf-8'))
            reader = csv.DictReader(content)
        except Exception as e:
            print(f"An error occurred while reading CSV file: {e}")
            return JSONResponse(content={"message": "An error occurred while reading CSV file"}, status_code=500)

        for row in reader:
            try:
                if 'Quantity' in row:
                    quantity = int(row['Quantity'])
                else:
                    quantity = row["QTY"]

                if 'Price' in row:
                    price_str = re.sub(r'[^\d.]', '', row['Price'])
                    if price_str:
                        price = float(price_str)
                    else:
                        price = 0.0
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
            except ValueError as e:
                print(f"An error occurred while processing order items: {e}")
                continue

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
            self.db_session.add(order_item_model)
        self.db_session.commit()
        return JSONResponse(content=order.id, status_code=201)

    def create_order(self, user_email: int):
        try:
            new_order = Order_Schema(date=datetime.now(), user_id=user_email)
            new_order_model = OrderModel(**new_order.model_dump())
            self.db_session.add(new_order_model)
            self.db_session.commit()
            self.db_session.refresh(new_order_model)  # Obtener el ID generado
            print(new_order)
            return new_order_model
        except Exception as e:
            print(f"An error occurred while creating order: {e}")
            return None

    def get_all_order(self):
        list_orders = []
        orders = self.db_session.query(OrderModel).all()

        if not orders:
            return JSONResponse(content={"message": "Order not found"}, status_code=404)

        for order in orders:
            order_individual = Order_Schema_Total.serialize_order_db(order)
            list_orders.append(order_individual)

        return JSONResponse(content=jsonable_encoder(list_orders), status_code=200)

    def import_order(self, date: str, order: dict, user_email: str):

        date = datetime.strptime(date, "%m/%d/%Y")
        if not date:
            return JSONResponse(content={"message": "Invalid date format"}, status_code=400)

        #Crear nueva orden para almacenar los order_items_model
        try:
            new_order = Order_Schema(date=order["date"], user_id=user_email)
            new_order_model = OrderModel(**new_order.model_dump())
            self.db_session.add(new_order_model)
            self.db_session.commit()
            self.db_session.refresh(new_order_model)
            id_order_created = new_order_model.id

        except ValidationError as ve:
            # Manejo de errores de validación de Pydantic
            print(f"Error de validación al crear la orden: {ve}")
            return JSONResponse(content={"message": "An error occurred while creating the order"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except IntegrityError:
            # Manejo de errores de integridad de la base de datos
            self.db_session.rollback()
            print(f"Error de integridad al crear la orden")
            return JSONResponse(content={"message": "An error occurred while creating the order"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        #Crear los order_items_model asociados a la orden
        for item in order.items:
            try:
                order_item = Order_Items_Schema(order_id=id_order_created, product_id=item["CustomerNumber"],
                                                quantity=item["Quantity"], price_per_unit=item["UnitPrice"],
                                                total=item["Subtotal"])
                order_item_model = OrderItemModel(**order_item.model_dump())
                self.db_session.add(order_item_model)
                self.db_session.commit()
            except ValidationError as ve:
                # Manejo de errores de validación de Pydantic
                print(f"Error de validación para el ítem {item}: {ve}")
                continue
            except IntegrityError:
                # Manejo de errores de integridad de la base de datos
                self.db_session.rollback()
                print(f"Error de integridad al procesar el ítem {item}")
                continue
            except Exception as e:
                # Manejo de errores generales
                self.db_session.rollback()
                print(f"Error al procesar el ítem {item}: {e}")
                return JSONResponse(content={"message": "An error occurred while processing order items"},
                                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JSONResponse(content={"message": "Order imported successfully", "order_id": id_order_created},
                            status_code=status.HTTP_201_CREATED)

    def edit_item_in_order(self, order_id: int, product_id: str, quantity: int):

        try:
            item = self.db_session.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).filter(
                OrderItemModel.product_id == product_id).first()

            if not item:
                return JSONResponse(content={"message": "Order item not found"}, status_code=404)

            elif quantity <= 0:
                self.db_session.delete(item)
                self.db_session.commit()
                return JSONResponse(content={"message": "Order item deleted successfully"}, status_code=200)

            else:
                item.quantity = quantity
                item.total = item.price_per_unit * quantity
                self.db_session.commit()
                return JSONResponse(content={"message": "Order item updated successfully"}, status_code=200)

        except SQLAlchemyError as e:
            print(f"An error occurred while editing order item: {e}")
            return JSONResponse(content={"message": "An error occurred while editing order item"}, status_code=500)
