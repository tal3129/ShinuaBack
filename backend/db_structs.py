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
from pydantic import BaseModel
from db_handler import db_handler, PRODUCT_COLLECTION, PICKUPS_COLLECTION, ORDERS_COLLECTION


# ProductStatus
COLLECTION = 0
STORAGE = 1


class BaseDB(BaseModel):
    did: str

    @staticmethod
    def COLLECTION_NAME():
        return NotImplementedError()
    
    @classmethod
    def read_from_db(cls, db_handler, did):
        return cls(did=did, **(db_handler.get_document(cls.COLLECTION_NAME(), did)))

    def _values_dict(self):
        values_dict = self.dict()
        values_dict.pop('did')
        return values_dict

    def add_to_db(self, db_handler):
        return db_handler.add_document(self.COLLECTION_NAME(), self._values_dict())

    def update_to_db(self, db_handler):
        return db_handler.set_document(self.COLLECTION_NAME(), self.did, self._values_dict())

    def delete_from_db(self, db_handler):
        return db_handler.delete_document(self.COLLECTION_NAME(), self.did)

class Product(BaseDB):
    name: str
    description: str
    image_url_list: List[str]
    status: int
    amount: int
    reserved: int

    @staticmethod
    def COLLECTION_NAME():
        return PRODUCT_COLLECTION

class Pickup(BaseDB):
    name: str
    address: str
    date: datetime
    products: List[int]

    @staticmethod
    def COLLECTION_NAME():
        return PICKUPS_COLLECTION

class Order(BaseDB):
    name: str
    address: str
    date: datetime
    ordered_products: List[Tuple[int, int]]

    @staticmethod
    def COLLECTION_NAME():
        return ORDERS_COLLECTION
