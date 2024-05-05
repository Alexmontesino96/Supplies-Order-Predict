import csv
from typing import List
from fastapi import UploadFile, File
from model.product_model import Product
from schema.product import Product_In_Schema, Product_Out_Schema
from db.db import Session
from io import BytesIO
import pandas as pd
from model.product_model import Product as ProductModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from model.order_item_model import OrderItemModel
from fastapi.responses import JSONResponse
import os   
import json
from enum import Enum

PRIORITY = json.loads(os.getenv('PRIORITY'))

class ProductServiceCSV:

    def __init__(self, db_session):
        self.db_session = db_session

    def get_products(self) -> List[Product_Out_Schema]:
        with self.db_session() as db:
            products = db.query(ProductModel).all()
            return products

    def import_list_month_product(self, file: UploadFile) -> List[Product]:
        content = BytesIO(file.file.read())
        df = pd.read_csv(content, skiprows=2)
        product_list = []
        df.fillna("", inplace=True)
        
        with self.db_session() as db:
            for index, row in df.iterrows():
                if not row['Item#']:
                    continue
                try:
                    new_product = Product_In_Schema(
                        id=row['Item#'].strip(),
                        name=row['Description'],
                        pack=row['Pack'],
                        uom=row['UOM'],
                        comments=row['Comments'],
                        price=0.0,
                        department_name="GROCERY"
                    )
                    if not new_product.name:
                        continue
                    new_product_out = Product_Out_Schema(**new_product.model_dump())
                    new_product_model = ProductModel(**new_product_out.model_dump())
                    db.add(new_product_model)
                    db.commit()  # Intenta hacer commit después de cada adición
                    product_list.append(new_product)
                except IntegrityError as e:
                    print(f"Error: No se pudo insertar el producto con ID {row['Item#']} debido a un error de integridad: {e}")
                    db.rollback()  # Revierte la transacción para este producto
                except Exception as e:
                    print(f"Error inesperado al insertar el producto con ID {row['Item#']}: {e}")
                    db.rollback()
                    
        return product_list
    
    def update_price(self) -> bool:
        with self.db_session() as db:
            products = db.query(ProductModel).all()
            for product_item in products:
                product_item_order = db.query(OrderItemModel).filter(OrderItemModel.product_id == product_item.id).first()
                if product_item_order:
                    product_item.price = product_item_order.price_per_unit
            db.commit()
            return JSONResponse(content={"message": "Price updated successfully"}, status_code=200)
        
    def get_products_by_id(self, id: str) -> Product_Out_Schema:
        with self.db_session() as db:
            products = db.query(ProductModel).filter(ProductModel.id == id).first()
            product_schema = Product_Out_Schema(**products.__dict__)
            if not product_schema:
                return JSONResponse(content={"message": "Product not found"}, status_code=404)
            return product_schema
        
    def delete_product(self, id: str) -> bool:
        with self.db_session() as db:
            product = db.query(ProductModel).filter(ProductModel.id == id).first()
            if product is None:
                return JSONResponse(content={"message": "Product not found"}, status_code=404)
            db.delete(product)
            db.commit()
            return JSONResponse(content={"message": "Product deleted successfully"}, status_code=200)
        
    def update_product(self, id: str, product: Product_In_Schema) -> bool:
        with self.db_session() as db:
            product = db.query(ProductModel).filter(ProductModel.id == id).first()
            if product is None:
                return JSONResponse(content={"message": "Product not found"}, status_code=404)
            product.name = product.name
            product.pack = product.pack
            product.uom = product.uom
            product.comments = product.comments
            product.price = product.price
            product.department_name = product.department_name
            db.commit()
            return JSONResponse(content={"message": "Product updated successfully"}, status_code=200)
