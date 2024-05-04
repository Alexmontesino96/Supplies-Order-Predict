from fastapi import FastAPI
from router.product_router import product_app
from db.db import Base, engine
from model.product_model import Product
from model.department_model import Department_Model
from schema.department import Departemnt_Schema
from router.order_router import order_app
from model.order_item_model import OrderItemModel
from db.db import Session
import os
from midleware.error_handler import ErrorHandlerMiddleware

app = FastAPI()
app.add_middleware(ErrorHandlerMiddleware)

Base.metadata.create_all(bind=engine)

app.include_router(product_app,)
app.include_router(order_app,)



'''department = os.getenv('DEPARTMENT')
if department:
    department = department.replace('["','').replace('"]','')
    for department in department.split('","'):
        with Session() as db:
            department = Departemnt_Schema(name=department)
            db.add(Department_Model(**department.model_dump()))
            db.commit()
            print(f"Department {department.name} created")
'''