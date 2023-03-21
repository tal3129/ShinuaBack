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

    def delete_from_db(self, db_handler):
        for o in db_handler.get_collection_dict(ORDERS_COLLECTION):
            if self.did in o.ordered_products:
                o.ordered_products.pop(self.did)
                o.update_to_db()
        for p in db_handler.get_collection_dict(PICKUPS_COLLECTION):
            if self.did in p.products:
                p.products.remove(self.did)
                p.update_to_db()
            
        return super().delete_document()

class Pickup(BaseDB):
    name: str
    address: str
    date: datetime
    products: Set[str]

    @staticmethod
    def COLLECTION_NAME():
        return PICKUPS_COLLECTION

class Order(BaseDB):
    name: str
    address: str
    description: str
    date: datetime
    ordered_products: Dict[str, int]

    def _is_pid_exists_in_order(self, pid):
        return pid in [i[0] for i in self.ordered_products]

    def edit_product_amount_in_order(self, db_handler, pid, amount):
        if not self._is_pid_exists_in_order(pid):
            return "Product doesnt exist in this order"
        product = Product.read_from_db(db_handler, pid)

        reserved_this_order = 0
        # Edit the selected tuple inside the list of tuples - goal nefesh
        for index, item in enumerate(self.ordered_products):
            itemlist = list(item)
            if itemlist[0] == pid:
                reserved_this_order = itemlist[1]
                if product.amount - product.reserved + reserved_this_order < amount:
                    return f"amount is too big, product have {product.amount} amount but {product.reserved} are reserved (while {itemlist[1]} reserved to this order)"
                itemlist[1] = amount
            item = tuple(itemlist)

            self.ordered_products[index] = item
        self.update_to_db(db_handler)
        product.reserved = product.reserved - reserved_this_order + amount
        product.update_to_db(db_handler)

        return 0

    def add_product(self, db_handler, pid, amount):
        if (self._is_pid_exists_in_order(pid)):
            return "Product already in order, consider editing the amount"
        product = Product.read_from_db(db_handler, pid)
        if product.amount - product.reserved < amount:
            return f"amount is too big, product have {product.amount} amount but {product.reserved} are reserved"
        self.ordered_products += (pid, amount)
        self.update_to_db(db_handler)

        product.reserved += amount
        product.update_to_db(db_handler)

        return 0

    def delete_from_db(self, db_handler):
        for pid, c in self.ordered_products:
            prod = Product.read_from_db(pid)
            prod.reserved -= c
            prod.update_to_db()
            
        return super().delete_document()

    @staticmethod
    def COLLECTION_NAME():
        return ORDERS_COLLECTION