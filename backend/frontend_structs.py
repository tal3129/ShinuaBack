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
from datetime import datetime
from typing import List

from pydantic import BaseModel

from db_structs import Product


class OrderedProduct(BaseModel):
    product: Product
    amount: int


class OrderResponse(BaseModel):
    did: str
    name: str
    address: str
    description: str
    date: datetime
    status: int
    ordered_products: List[OrderedProduct]
