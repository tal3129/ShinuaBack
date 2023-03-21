"""
This file handles all the routes (relevant to backend)
Should only route requests from frontend and communicate with backend logic to return PYDANTIC objects
"""

from fastapi import FastAPI
from db_structs import Product, Order, Pickup, PRODUCT_COLLECTION, PICKUPS_COLLECTION, ORDERS_COLLECTION
from db_handler import db_handler, get_all_products, get_all_orders, get_all_pickups

app = FastAPI()
firestore_db = db_handler()

# DATA RETRIEVERS

@app.get("/get_catalog")
def get_products():
    return get_all_products(firestore_db)

@app.get("/get_orders")
def get_orders():
    return get_all_orders(firestore_db)

@app.get("/get_pickups")
def get_pickups():
    return get_all_pickups(firestore_db)

@app.get("/get_product/{pid}")
def get_product_by_id(pid: str):
    return Product.read_from_db(firestore_db, pid)


# DATA EDITORS - TODO, return success or error

@app.post("/edit_product")
def edit_product(Product: Product):
    Product.update_to_db(firestore_db)
    return {}

@app.post("/edit_order")
def edit_order(Order: Order):
    Order.update_to_db(firestore_db)
    return {}

@app.post("/edit_pickup")
def edit_pickup(Pickup: Pickup):
    Pickup.update_to_db(firestore_db)
    return {}