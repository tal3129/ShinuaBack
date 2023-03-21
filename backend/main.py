"""
This file handles all the routes (relevant to backend)
Should only route requests from frontend and communicate with backend logic to return PYDANTIC objects
"""

from fastapi import FastAPI
from db_structs import Product, Order, Pickup
from db_handler import db_handler, PRODUCT_COLLECTION, PICKUPS_COLLECTION, ORDERS_COLLECTION

app = FastAPI()
firestore_db = db_handler()

# DATA RETRIEVERS

@app.get("/catalog")
def get_products():
    return firestore_db.get_collection(PRODUCT_COLLECTION)

@app.get("/orders")
def get_orders():
    return firestore_db.get_collection(ORDERS_COLLECTION)

@app.get("/pickups")
def get_pickups():
    return firestore_db.get_collection(PICKUPS_COLLECTION)


# DATA EDITORS

@app.post("/set_product")
def add_product(Product: Product):
    # We need upload image option with add
    return "WORKED OR NOT BEACH"

@app.post("/set_order")
def add_order(Order: Order):
    return "WORKED OR NOT BEACH"

@app.post("/set_pickup")
def add_pickup(Pickup: Pickup):
    return "WORKED OR NOT BEACH"