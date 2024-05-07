from fastapi.routing import APIRouter
from fastapi import Depends, Security
from db.db import session_scope as Session
from model.product_model import Product as Product_Model
from schema.product import Product_In_Schema, Product_Out_Schema
from fastapi.security import HTTPBearer
from application.auth import auth
from fastapi_auth0 import Auth0User
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from service.product_service_csv import ProductServiceCSV
from fastapi import UploadFile, File
from fastapi import status



product_app = APIRouter()
token_auth_schema = HTTPBearer()

@product_app.get("/products/get_all", tags=["Product"], dependencies=[Depends(auth.implicit_scheme)])
def get_all_products(user: Auth0User = Security(auth.get_user)):
    """
    Get all products.

    Parameters:
    - user: Auth0User object representing the authenticated user.

    Returns:
    - list[Product_Out_Schema]: A list of product objects.
    """
    products = ProductServiceCSV(Session).get_products()
    return jsonable_encoder(products)

@product_app.post("/products", tags=["Product"], dependencies=[Depends(auth.implicit_scheme)])
def import_product_month_csv(product_month_csv: UploadFile = File, user: Auth0User = Security(auth.get_user))-> list[Product_In_Schema]:
    """
    Endpoint for importing a CSV file containing product data for a specific month.

    Parameters:
    - product_month_csv (UploadFile): The CSV file containing the product data.
    - user (Auth0User): The authenticated user making the request.

    Returns:
    - dict: A dictionary containing the imported product data.

    Raises:
    - HTTPException: If there is an error during the import process.
    """
    product_dict = ProductServiceCSV(Session).import_list_month_product(product_month_csv)
    return jsonable_encoder(product_dict)

@product_app.get("/products/search_product{id}", tags=["Product"], dependencies=[Depends(auth.implicit_scheme)])
def search_products_by_id(id: str, user: Auth0User = Security(auth.get_user))-> Product_Out_Schema:
    """
    Search for a product by ID.

    Parameters:
    - id (str): The ID of the product to search for.
    - user (Auth0User): The authenticated user making the request.

    Returns:
    - Product_Out_Schema: The product object with the specified ID.
    """
    product = ProductServiceCSV(Session).get_products_by_id(id)
    if not product:
        return JSONResponse(content={"message": "Product not found"}, status_code=404)
    return JSONResponse(content=jsonable_encoder(product), status_code=200)


@product_app.delete("/products/delete_product{id}", tags=["Product"], dependencies=[Depends(auth.implicit_scheme)])
def delete_product(id: str, user: Auth0User = Security(auth.get_user))-> JSONResponse:
    """
    Delete a product.

    Parameters:
    - user: Auth0User object representing the authenticated user.

    Returns:
    - The result of the ProductServiceCSV's delete_product() method.
    """
    return ProductServiceCSV(Session).delete_product(id)

@product_app.put("/products/update_product{id}", tags=["Product"], dependencies=[Depends(auth.implicit_scheme)])
def update_product(id: str, product: Product_In_Schema, user: Auth0User = Security(auth.get_user))-> JSONResponse:
    """
    Update a product.

    Parameters:
    - user: Auth0User object representing the authenticated user.

    Returns:
    - The result of the ProductServiceCSV's update_product() method.
    """
    return ProductServiceCSV(Session).update_product(id, product)
