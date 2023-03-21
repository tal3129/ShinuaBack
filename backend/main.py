"""
This file handles all the routes (relevant to backend)
Should only route requests from frontend and communicate with backend logic to return PYDANTIC objects
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from db_structs import Product, Order, Pickup
from db_handler import db_handler, get_all_products, get_all_orders, get_all_pickups

app = FastAPI()
firestore_db = db_handler()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# INFO

@app.get("/", response_class=HTMLResponse)
def get_info():
    return """<html>
    <head>
        <title>sup g</title>
    </head>
    <body>
        <h1>Available Routes:</h1>
        <h3>/get_catalog</h3>
        <h3>/get_orders</h3>
        <h3>/get_pickups</h3>
        <h3>/get_product/{pid}</h3>
        <h3>/edit_product</h3>
        <h3>/edit_order</h3>
        <h3>/edit_pickup</h3>
    </body>
</html>
        """

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


# DATA EDITORS

@app.post("/edit_product")
def edit_product(Product: Product):
    return Product.update_to_db(firestore_db)

@app.post("/edit_order")
def edit_order(Order: Order):
    return Order.update_to_db(firestore_db)

@app.post("/edit_pickup")
def edit_pickup(Pickup: Pickup):
    return Pickup.update_to_db(firestore_db)