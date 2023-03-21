"""
## DB
Product:
- id
- Name
- Description
- Image Url List
- Status
- Amount
- Reserved= number of product in orders.

Pickup
- Name
- Address
- Date
- Products: List[ID]

Order:
- Name
- Address
- Date
- OrderedProducts: List[(ID,Amount)]
"""
from datetime import datetime
from dataclasses import field, asdict
from typing import List, Union, Tuple
from fastapi import FastAPI
from pydantic.dataclasses import dataclass
from db_handler import db_handler

# Collection names
PRODUCT_COLLECTION = "Products"
PICKUPS_COLLECTION = "Orders"
ORDERS_COLLECTION = "Pickups"


# ProductStatus
COLLECTION = 0
STORAGE = 1


@dataclass
class BaseDB:
    did: str = ""

    COLLECTION_NAME = ""

    @classmethod
    def read_from_db(cls, db_handler, did):
        return cls(**db_handler.get_document(cls.COLLECTION_NAME, did))

    def _to_dict(self):
        values_dict = asdict(self)
        values_dict.pop('did')
        return values_dict

    def add_to_db(self, db_handler):
        return self.db_handler.add_document(self.COLLECTION_NAME, self._to_dict())

    def update_to_db(self, db_handler):
        return self.db_handler.set_document(self.COLLECTION_NAME, self.did, self._to_dict())



class Product(BaseDB):
    name: str
    description: str
    image_url_list: List[str]
    status: int
    amount: int
    reserved: int

    COLLECTION_NAME = PRODUCT_COLLECTION

@dataclass
class Pickup(BaseDB):
    name: str
    address: str
    date: datetime
    products: List[int]

    COLLECTION_NAME = PICKUPS_COLLECTION


@dataclass
class Order(BaseDB):
    name: str
    address: str
    date: datetime
    ordered_products: List[Tuple[int, int]]

    COLLECTION_NAME = ORDERS_COLLECTION
