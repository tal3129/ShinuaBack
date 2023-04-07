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
from enum import IntEnum
from typing import List, Dict, Set, Optional
from pydantic import BaseModel
from fastapi import HTTPException


# Collection names
PRODUCT_COLLECTION = "Products"
PICKUPS_COLLECTION = "Pickups"
ORDERS_COLLECTION = "Orders"


# ProductStatus
class ProductStatus(IntEnum):
    COLLECTION = 0
    STORAGE = 1


# OrderStatus
class OrderStatus(IntEnum):
    ORDER_IN_PROGRESS = 0
    ORDER_DONE = 1


class BaseDB(BaseModel):
    did: Optional[str] = None

    @staticmethod
    def COLLECTION_NAME():
        return NotImplementedError()

    @classmethod
    def read_from_db(cls, db_handler, did):
        doc = db_handler.get_document(cls.COLLECTION_NAME(), did)
        if doc is None:
            raise HTTPException(status_code=404, detail='Document not found')
        return cls(did=did, **doc)

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

    def move_to_inventory(self, db_handler):
        self.status = ProductStatus.STORAGE

        # Delete from pickups
        pickups = db_handler.get_collection_dict(PICKUPS_COLLECTION)
        for pickup_dict in pickups["Pickups"]:
            if self.did in pickup_dict["products"]:
                pickup = Pickup.read_from_db(db_handler, pickup_dict["did"])
                pickup.products.remove(self.did)
                pickup.update_to_db(db_handler)
                break

        self.update_to_db(db_handler)
        return 0

    @staticmethod
    def COLLECTION_NAME():
        return PRODUCT_COLLECTION

    @staticmethod
    def is_exists(db_handler, pid):
        pids = db_handler.get_collection(PRODUCT_COLLECTION).stream()
        for p in pids:
            if p.id == pid:
                return True
        return False

    def delete_from_db(self, db_handler):
        orders = db_handler.get_collection_dict(ORDERS_COLLECTION)
        for order_dict in orders["Orders"]:
            if self.did in order_dict['ordered_products']:
                order = Order.read_from_db(db_handler, order_dict["did"])
                order.ordered_products.pop(self.did)
                order.update_to_db(db_handler)

        pickups = db_handler.get_collection_dict(PICKUPS_COLLECTION)
        for pickup_dict in pickups["Pickups"]:
            if self.did in pickup_dict["products"]:
                pickup = Pickup.read_from_db(db_handler, pickup_dict["did"])
                pickup.products.remove(self.did)
                pickup.update_to_db(db_handler)

        return super().delete_from_db(db_handler)

    def recalculate_reserved(self, db_handler):
        orders = db_handler.get_collection_dict(ORDERS_COLLECTION)
        self.reserved = 0
        for order_dict in orders["Orders"]:
            if self.did in order_dict['ordered_products']:
                self.reserved += order_dict['ordered_products'][self.did]
        self.update_to_db(db_handler)


class Pickup(BaseDB):
    name: str
    address: str
    date: datetime
    products: Set[str]

    @staticmethod
    def COLLECTION_NAME():
        return PICKUPS_COLLECTION

    def move_to_inventory(self, db_handler):
        """
        Move all products to inventory and delete pickup
        :param db_handler: DBHandler
        :return:
        """
        for pid in self.products:
            prod = Product.read_from_db(db_handler, pid)
            prod.move_to_inventory(db_handler)
        self.delete_from_db(db_handler)
        return 0

    def delete_with_products(self, db_handler):
        """
        Delete pickup and all products
        :param db_handler: DBHandler
        :return:
        """
        for pid in self.products:
            prod = Product.read_from_db(db_handler, pid)
            prod.delete_from_db(db_handler)
        self.delete_from_db(db_handler)
        return 0


class Order(BaseDB):
    name: str
    address: str
    description: str
    date: datetime
    ordered_products: Dict[str, int]
    status: int

    def mark_as_done(self, db_handler):
        """
        Mark order as done, and update products amount
        :param db_handler: DBHandler
        :return:
        """
        for pid, c in self.ordered_products.items():
            prod = Product.read_from_db(db_handler, pid)
            prod.amount -= c
            prod.reserved -= c
            prod.update_to_db(db_handler)

        self.status = OrderStatus.ORDER_DONE
        self.update_to_db(db_handler)
        return 0

    def add_product(self, db_handler, pid, amount):
        if not Product.is_exists(db_handler, pid):
            return "Product doesnt exist!"

        prev_amount = 0
        if pid in self.ordered_products:
            prev_amount = self.ordered_products[pid]
        product = Product.read_from_db(db_handler, pid)

        if product.amount - product.reserved + prev_amount < amount:
            return f"amount is too big, product have {product.amount} amount but {product.reserved} are reserved (while {prev_amount} reserved to this order)"
        self.ordered_products[pid] = amount
        self.update_to_db(db_handler)

        product.reserved = product.reserved - prev_amount + amount
        product.update_to_db(db_handler)

        return 0

    def delete_from_db(self, db_handler):
        result = super().delete_from_db(db_handler)

        for product_id, _ in self.ordered_products.items():
            product = Product.read_from_db(db_handler, product_id)
            product.recalculate_reserved(db_handler)
        return result

    @staticmethod
    def COLLECTION_NAME():
        return ORDERS_COLLECTION
