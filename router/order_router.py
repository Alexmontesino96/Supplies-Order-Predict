from fastapi import APIRouter
from fastapi.security import HTTPBearer
from fastapi import Depends, Security
from application.auth import auth
from fastapi_auth0 import Auth0User
from service.order_service import Order_Service
from fastapi import UploadFile, File
from db.db import Session
from fastapi.responses import JSONResponse


order_app = APIRouter()
token_auth_schema = HTTPBearer()

@order_app.get("/orders/search_order_by_id", dependencies= [Depends(auth.implicit_scheme)], tags=["Order"])
def search_order_by_id(order_id: int, user: Auth0User = Security(auth.get_user)):
    return Order_Service(Session).search_order_by_id(order_id)

@order_app.post("/orders/import_order", dependencies= [Depends(auth.implicit_scheme)], tags=["Order"])
def import_order(csv_file : UploadFile = File (...),user: Auth0User = Security(auth.get_user)):

    status, content = Order_Service(Session).process_order_csv(user_id= user.id,csv_file= csv_file)
    if status == 500:
        return {"message": "An error occurred while processing order items"}
    else:
        return JSONResponse(content={"message": "Order imported successfully", "order_id": content}, status_code=201)
    
@order_app.delete("/orders/delete-product-in-order", dependencies= [Depends(auth.implicit_scheme)], tags=["Order"])
def delete_product_in_order(product_id:int, order_id: int, user: Auth0User = Security(auth.get_user)):
    Order_Service(Session).delete_items_from_order(product_id, order_id)
    return JSONResponse(content={"message": "Order items deleted successfully"}, status_code=200)

@order_app.post("/orders/add_product_to_order", dependencies= [Depends(auth.implicit_scheme)], tags=["Order"])
def add_product_to_order(order_id: int, product_id: int , user: Auth0User = Security(auth.get_user)):
    Order_Service(Session).add_product_to_order(product_id, order_id)
    return JSONResponse(content={"message": "Product added to order successfully"}, status_code=201)