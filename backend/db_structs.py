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
from typing import List, Dict
from pydantic import BaseModel

# Collection names
PRODUCT_COLLECTION = "Products"
PICKUPS_COLLECTION = "Pickups"
ORDERS_COLLECTION = "Orders"

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
    origin: str

    @staticmethod
    def COLLECTION_NAME():
        return PRODUCT_COLLECTION

class Pickup(BaseDB):
    name: str
    address: str
    date: datetime
    products: List[str]

    @staticmethod
    def COLLECTION_NAME():
        return PICKUPS_COLLECTION

class Order(BaseDB):
    name: str
    address: str
    description: str
    date: datetime
    ordered_products: Dict[str, int]

    def edit_product_amount_in_order(self, db_handler, pid, amount):
        if pid not in self.ordered_products:
            return "Product doesnt exist in this order"
        product = Product.read_from_db(db_handler, pid)

        prev_amount = self.ordered_products[pid]
        if product.amount - product.reserved + prev_amount < amount:
            return f"amount is too big, product have {product.amount} amount but {product.reserved} are reserved (while {prev_amount} reserved to this order)"
        
        self.ordered_products[pid] = amount
        self.update_to_db(db_handler)
        product.reserved = product.reserved - prev_amount + amount
        product.update_to_db(db_handler)

        return 0

    def add_product(self, db_handler, pid, amount):
        if pid in self.ordered_products:
            return "Product already in order, consider editing the amount"
        product = Product.read_from_db(db_handler, pid)
        if product.amount - product.reserved < amount:
            return f"amount is too big, product have {product.amount} amount but {product.reserved} are reserved"
        self.ordered_products[pid] = amount
        self.update_to_db(db_handler)

        product.reserved += amount
        product.update_to_db(db_handler)

        return 0

    @staticmethod
    def COLLECTION_NAME():
        return ORDERS_COLLECTION