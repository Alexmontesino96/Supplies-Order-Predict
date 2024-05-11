import json
import os
from io import BytesIO
from typing import List

import pandas as pd
from fastapi import UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from model.order_item_model import OrderItemModel
from model.product_model import Product as ProductModel
from schema.product import Product_In_Schema, Product_Out_Schema

PRIORITY = json.loads(os.getenv('PRIORITY'))


class ProductServiceCSV:

    def __init__(self, db_session):
        self.db_session = db_session

    def get_products(self) -> List[Product_Out_Schema]:
        products = self.db_session.query(ProductModel).all()
        return products

    def import_list_month_product(self, file: UploadFile) -> List[Product_In_Schema]:
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
                    db.add(new_product_model)  # Intenta hacer commit después de cada adición
                    product_list.append(new_product)
                except IntegrityError as e:
                    print(
                        f"Error: No se pudo insertar el producto con ID {row['Item#']} debido a un error de integridad: {e}")
                    db.rollback()  # Revierte la transacción para este producto
                except Exception as e:
                    print(f"Error inesperado al insertar el producto con ID {row['Item#']}: {e}")
                    db.rollback()
            db.commit()

        return product_list

    def update_price(self) -> JSONResponse:
        with self.db_session() as db:
            products = db.query(ProductModel).all()
            for product_item in products:
                product_item_order = db.query(OrderItemModel).filter(
                    OrderItemModel.product_id == product_item.id).first()
                if product_item_order:
                    product_item.price = product_item_order.price_per_unit
            db.commit()
            return JSONResponse(content={"message": "Price updated successfully"}, status_code=200)

    def get_products_by_id(self, product_id: str) -> JSONResponse | ProductModel:
        with self.db_session() as db:
            products = db.query(ProductModel).filter(ProductModel.id == product_id).first()
            if not products:
                return JSONResponse(content={"message": "Product not found"}, status_code=404)
            return products

    def delete_product(self, product_id: str) -> JSONResponse:
        with self.db_session() as db:
            product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
            if product is None:
                return JSONResponse(content={"message": "Product not found"}, status_code=404)
            db.delete(product)
            db.commit()
            return JSONResponse(content={"message": "Product deleted successfully"}, status_code=200)

    def update_product(self, product_id: str, product: Product_In_Schema) -> JSONResponse:

        product_for_edit = self.db_session.query(ProductModel).filter(ProductModel.id == product_id).first()
        if product is None:
            return JSONResponse(content={"message": "Product not found"}, status_code=404)
        else:
            product_for_edit.name = product.name
            product_for_edit.pack = product.pack
            product_for_edit.uom = product.uom
            product_for_edit.comments = product.comments
            product_for_edit.price = product.price
            product_for_edit.department_name = product.department_name
            self.db_session.commit()
        return JSONResponse(content={"message": "Product updated successfully"}, status_code=200)
