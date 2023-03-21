"""
This file handles all the routes (relevant to backend)
Should only route requests from frontend and communicate with backend logic to return PYDANTIC objects
"""

from fastapi import FastAPI
from db_structs import Product, Order, Pickup
from db_handler import db_handler, PRODUCT_COLLECTION, PICKUPS_COLLECTION, ORDERS_COLLECTION

app = FastAPI()
firestore_db = db_handler()

@app.get("/catalog")
def get_products():
    return firestore_db.get_collection(PRODUCT_COLLECTION)

@app.get("/orders")
def get_orders():
    return firestore_db.get_collection(ORDERS_COLLECTION)

@app.get("/pickups")
def get_pickups():
    return firestore_db.get_collection(PICKUPS_COLLECTION)