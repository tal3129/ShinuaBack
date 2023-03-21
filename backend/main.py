"""
This file handles all the routes (relevant to backend)
Should only route requests from frontend and communicate with backend logic to return PYDANTIC objects
"""

from fastapi import FastAPI
from db_structs import Product, Order, Pickup, PRODUCT_COLLECTION, PICKUPS_COLLECTION, ORDERS_COLLECTION
from db_handler import db_handler

app = FastAPI()
firestore_db = db_handler()

# DATA RETRIEVERS

@app.get("/get_catalog")
def get_products():
    return firestore_db.get_collection(PRODUCT_COLLECTION)

@app.get("/get_orders")
def get_orders():
    return firestore_db.get_collection(ORDERS_COLLECTION)

@app.get("/get_pickups")
def get_pickups():
    return firestore_db.get_collection(PICKUPS_COLLECTION)

@app.get("/get_product/{pid}")
def get_product_by_id(pid: int):
    return Product.read_from_db(pid)


# DATA EDITORS

@app.post("/edit_product")
def edit_product(Product: Product):
    return firestore_db.set_document(PRODUCT_COLLECTION, Product.did, Product)

@app.post("/edit_order")
def edit_order(Order: Order):
    return firestore_db.set_document(ORDERS_COLLECTION, Order.did, Order)

@app.post("/edit_pickup")
def edit_pickup(Pickup: Pickup):
    return firestore_db.set_document(PICKUPS_COLLECTION, Pickup.did, Pickup)