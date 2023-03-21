"""
This file handles all the routes (relevant to backend)
Should only route requests from frontend and communicate with backend logic to return PYDANTIC objects
"""

from fastapi import FastAPI
from pydantic.dataclasses import dataclass

app = FastAPI()

@app.get("/")
def root():
    # should return the main frontend page
    return "HELLO WORLD"


@app.post("/catalog")
def get_products(): # should be product from db_structs.py WITH db_logic.py
    return "he" # blablabla

@app.post("/orders")
def get_orders(item: Item): # should be order from db_structs.py WITH db_logic.py
    return item

@app.post("/pickups")
def create_item(item: Item): # should be pickup from db_structs.py WITH db_logic.py
    return item