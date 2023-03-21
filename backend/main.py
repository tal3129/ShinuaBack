"""
This file handles all the routes (relevant to backend)
Should only route requests from frontend and communicate with backend logic to return PYDANTIC objects
"""

from fastapi import FastAPI
from db_structs import Product, Order, Pickup
from db_handler import db_handler

app = FastAPI()

@app.get("/catalog")
def get_products(): # should be product from db_structs.py WITH db_logic.py
    return "he" # blablabla

@app.get("/orders")
def get_orders(item: Item): # should be order from db_structs.py WITH db_logic.py
    return item

@app.get("/pickups")
def get_pickups(item: Item): # should be pickup from db_structs.py WITH db_logic.py
    return item