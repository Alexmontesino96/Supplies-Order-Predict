from typing import List
from pydantic import BaseModel, Field, validator, computed_field
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from model.order_model import OrderModel
from db.db import Session
from model.department_model import Department_Model
from datetime import timedelta
from schema.department import Departemnt_Schema
from typing import Optional
from enum import Enum
from typing import Union




load_dotenv()
DEPARTMENT = json.loads(os.getenv('DEPARTMENT'))
PRIORITY = json.loads(os.getenv('PRIORITY'))

class Priority_Level(Enum):
    LOW = PRIORITY[0]
    MEDIUM = PRIORITY[1]
    HIGH = PRIORITY[2]

class Product_In_Schema(BaseModel):
    id : str
    name: str
    pack: str
    uom: str
    comments: str = Field(default=None)
    price: float = Field(default = 0.0)
    department_name: str = Field(default=None)

    model_config = {
        'json_schema_extra': {
            'example': {
                'id': '1',
                'name': 'Deli Container 16oz',
                'pack': '100',
                'uom': 'CS',
                'comments': 'This is a product',
                'price': 10.0,
                'department_name': ["FRONT-END","DELI","CMS","MEAT","SEAFOOD","BAKERY","PRODUCE","GROCERY","DAIRY","FROZEN","BEER-WINE","PHARMACY","FLORAL"]
            }
        }
    }




class Product_Out_Schema(Product_In_Schema):
    active: bool = Field(default=True)
    date_active: datetime = Field(default_factory=datetime.now)
    date_deactive: Optional[datetime] = Field(default=None, init=False)
    priority: Priority_Level = Field(default=Priority_Level.MEDIUM)

    model_config = {
        'json_schema_extra': {
            'example': {
                'id': '1',
                'name': 'Deli Container 16oz',
                'pack': '100',
                'uom': 'CS',
                'comments': 'This is a product',
                'price': 10.0,
                'department_name': ["FRONT-END","DELI","CMS","MEAT","SEAFOOD","BAKERY","PRODUCE","GROCERY","DAIRY","FROZEN","BEER-WINE","PHARMACY","FLORAL"],
                'active': True,
                'date_active': '2021-07-01T00:00:00',
                'date_deactive': None,
                'priority': 'MEDIUM'
            }
        }
    }

    @classmethod
    def serialize_product_db(cls, product):
        return cls(
            id=product.id,
            name=product.name,
            pack=product.pack,
            uom=product.uom,
            comments=product.comments,
            price=product.price,
            department_name=product.department_name,
            active=product.active,
            date_active=product.date_active,
            date_deactive=product.date_deactive,
            priority=product.priority
        )

    """@computed_field
    @property
    def week_average_last_30_days(self)-> Union[float, None]:

        product_in_orders = []
        count = 0
        average = 0

        with Session() as db:
            orders = db.query(OrderModel).filter(OrderModel.date >= datetime.now() - timedelta(days=30)).all()
            print(orders)
            if len(orders) > 5:

                for order in orders: 
                    for product in order.order_items:

                        if product.product_id == self.id:
                            product_in_orders.append(product.quantity)
                            count += 1
                            if count == 0:
                                return average 
                if count > 0:
                    average = sum(product_in_orders) / count
            
            elif len(orders) == 0:
                return None

            return average"""
            

    @classmethod
    def deactivate(self):
        self.active = False
        self.date_deactive = datetime.now()

    @classmethod
    def activate(self):
        self.active = True
        self.date_active = datetime.now()
        self.date_deactive = None
    


    @validator('department_name', pre=True)
    def validate_department(cls, value):
        # Asegurarse de obtener el nombre del departamento como una cadena
        department_name = value['name'] if isinstance(value, dict) else value
        print(department_name)
        with Session() as db:
            # Intenta encontrar el departamento con ese nombre
            department = db.query(Department_Model).filter(Department_Model.name == department_name).first()
            print("Encontre el departamento")
            if department:
                return department_name
            else:
                raise ValueError("Department not found")
    