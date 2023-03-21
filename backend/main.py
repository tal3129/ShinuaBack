"""
This file handles all the routes (relevant to backend)

Should only route requests from frontend and communicate with backend logic to return PYDANTIC objects
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic.dataclasses import dataclass

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/catalog")
def get_item(item: Item): # should be product from db_structs.py WITH db_logic.py
    return item

@app.post("/orders")
def create_item(item: Item): # should be order from db_structs.py WITH db_logic.py
    return item

@app.post("/pickups")
def create_item(item: Item): # should be pickup from db_structs.py WITH db_logic.py
    return item