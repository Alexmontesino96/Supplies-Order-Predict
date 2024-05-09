from datetime import datetime
from fastapi import APIRouter
from fastapi.security import HTTPBearer
from fastapi import Depends, Security
from application.auth import auth
from fastapi_auth0 import Auth0User
from service.order_service import Order_Service
from fastapi import UploadFile, File
from db.db import session_scope
from fastapi.responses import JSONResponse

order_app = APIRouter()
token_auth_schema = HTTPBearer()


@order_app.get("/orders/search_order_by_id", dependencies=[Depends(auth.implicit_scheme)], tags=["Order"])
def search_order_by_id(order_id: int, user: Auth0User = Security(auth.get_user)):
    with session_scope() as Session:
        return Order_Service(Session).search_order_by_id(order_id)


@order_app.get("/orders/get-all-order", dependencies=[Depends(auth.implicit_scheme)], tags=["Order"])
def get_all_order(user: Auth0User = Security(auth.get_user)):
    with session_scope() as Session:
        return Order_Service(Session).get_all_order()


@order_app.post("/orders/import_order_csv", dependencies=[Depends(auth.implicit_scheme)], tags=["Order"])
def import_order(date: str, csv_file: UploadFile = File(...), user: Auth0User = Security(auth.get_user)):
    with session_scope() as Session:

        date = datetime.strptime("04/23/2021", "%m/%d/%Y")
        if not date:
            return JSONResponse(content={"message": "Invalid date format"}, status_code=400)

        return Order_Service(Session).import_order(date, csv_file)


@order_app.delete("/orders/delete-product-in-order", dependencies=[Depends(auth.implicit_scheme)], tags=["Order"])
def delete_product_in_order(product_id: str, order_id: int, user: Auth0User = Security(auth.get_user)):
    with session_scope() as Session:
        Order_Service(Session).edit_item_in_order(order_id, product_id, 0)


@order_app.post("/orders/add_product_to_order", dependencies=[Depends(auth.implicit_scheme)], tags=["Order"])
def add_product_to_order(order_id: int, product_id: str, quantity: int, user: Auth0User = Security(auth.get_user)):
    with session_scope() as Session:
        return Order_Service(Session).add_product_to_order(product_id, order_id, quantity)


@order_app.post("/orders/import_order", dependencies=[Depends(auth.implicit_scheme)], tags=["Order"])
def import_order(date: str, order: dict, user: Auth0User = Security(auth.get_user)):
    with session_scope() as Session:
        return Order_Service(Session).import_order(date, order, user.email)


@order_app.put("/orders/edit_item", dependencies=[Depends(auth.implicit_scheme)], tags=["Order"])
def edit_item(order_id: int, product_id: str, quantity: int, user: Auth0User = Security(auth.get_user)):
    with session_scope() as Session:
        return Order_Service(Session).edit_item_in_order(order_id, product_id, quantity)
