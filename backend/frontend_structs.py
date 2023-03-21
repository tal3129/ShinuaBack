"""
## From backend API for Frontend:
Product:
- id
- Name
- Description
- Image Url List
- Status
- Amount
- Origin = "WeWork Herzylia"

Pickups:
- Name
- Address
- Date
- Products: List [{
	- ID
	- Name
	- Description
	- Image Url List
	- Amount
}]

Orders:
- Name
- Address
- ProductCounts: List [{
	- ID
	- Name
	- Description
	- Image Url List
	- Amount (in order)
}]
"""

from enum import Enum
from datetime import datetime
from dataclasses import field 
from typing import List, Union, Tuple
from fastapi import FastAPI
from pydantic.dataclasses import dataclass
from db_structs import ProductStatus

@dataclass
class Product:
    pid: int
    name: str
    description: str
    image_url_list: List[str]
    status: ProductStatus
    amount: int
    origin: str

@dataclass
class Pickup():
    name: str
    address: str
    date: datetime
    products: List[int]
