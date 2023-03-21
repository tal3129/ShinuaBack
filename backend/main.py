"""
This file handles all the routes (relevant to backend)
Should only route requests from frontend and communicate with backend logic to return PYDANTIC objects
"""

from fastapi import FastAPI, Body
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
        <h3>go to /docs for nice nice nice</h3>
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

@app.post("/edit_product_amount_in_order")
def edit_product_amount_in_order(pid:str = Body(...),
                                 oid:str = Body(...), 
                                 amount: int = Body(...)):
    order = Order.read_from_db(firestore_db, oid)
    return order.edit_product_amount_in_order(firestore_db, pid, amount)

# DATA ADDERS

@app.post("/add_product")
def add_product(Product: Product):
    return Product.add_to_db(firestore_db)

@app.post("/add_pickup")
def add_pickup(Pickup: Pickup):
    return Pickup.add_to_db(firestore_db)

@app.post("/add_order")
def add_order(Order: Order):
    return Order.add_to_db(firestore_db)

@app.post("/add_product_to_order")
def add_product_to_order(pid: str = Body(...), 
                         oid: str = Body(...), 
                         amount: int = Body(...)):
    order = Order.read_from_db(firestore_db, oid)
    return order.add_product(firestore_db, pid, amount)

# DATA DELETORS

@app.post("/delete_product")
def delete_product(Product: Product):
    return Product.delete_from_db(firestore_db)

@app.post("/delete_pickup")
def delete_product(Pickup: Pickup):
    return Pickup.delete_from_db(firestore_db)

@app.post("/delete_order")
def delete_product(Order: Order):
    return Order.delete_from_db(firestore_db)

# STATUS CHANGERS
@app.post("/move_product_to_inventory")
def move_product_to_inventory(pid: str = Body(..., embed=True)):
    product = Product.read_from_db(firestore_db, pid)
    return product.move_to_inventory(firestore_db)

@app.post("/mark_order_as_done")
def nark_order_as_done(oid: str = Body(..., embed=True)):
    order = Order.read_from_db(firestore_db, oid)
    return order.move_to_inventory(firestore_db)