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
from enum import Enum
from datetime import datetime
from dataclasses import field 
from typing import List, Union, Tuple
from fastapi import FastAPI
from pydantic.dataclasses import dataclass


class ProductStatus(Enum):
    COLLECTION = 0
    STORAGE = 1


@dataclass
class Product:
    pid: int
    name: str
    description: str
    image_url_list: List[str]
    status: ProductStatus
    amount: int
    reserved: int

    def read_from_db():
        pass

    def update_to_db():
        pass


@dataclass
class Pickup:
    pid: int
    name: str
    address: str
    date: datetime
    products: List[int]

    def read_from_db():
        pass

    def update_to_db():
        pass 


@dataclass
class Order:
    oid: int
    name: str
    address: str
    date: datetime
    ordered_products: List[Tuple(int, int)]

    def read_from_db():
        pass

    def update_to_db():
        pass 