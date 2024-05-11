from fastapi import FastAPI
from router.product_router import product_app
from db.db import Base, engine
from router.order_router import order_app
from midleware.error_handler import ErrorHandlerMiddleware

app = FastAPI()
app.add_middleware(ErrorHandlerMiddleware)

Base.metadata.create_all(bind=engine)

app.include_router(product_app, )
app.include_router(order_app)
