"""
This file handles all the routes (relevant to backend)
Should only route requests from frontend and communicate with backend logic to return PYDANTIC objects
"""

from fastapi import FastAPI, Body, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List
from db_structs import Product, Order, Pickup
from db_handler import db_handler, get_all_products, get_all_orders, get_all_pickups
from export_to_pdf import prepare_order_for_export, export_to_pdf

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
    orders = get_all_orders(firestore_db)['Orders']
    for o in orders:
        keys = o["ordered_products"].keys()
        res = []
        for pid in keys:
            res.append(Product.read_from_db(firestore_db, pid).dict())
        o["ordered_products"] = res 
    return orders

@app.get("/get_pickups")
def get_pickups():
    pickups = get_all_pickups(firestore_db)['Pickups']
    for p in pickups:
        res = []
        for pid in p["products"]:
            res.append(Product.read_from_db(firestore_db, pid).dict())
        p["products"] = res
    return pickups

@app.get("/get_product/{pid}")
def get_product_by_id(pid: str):
    return Product.read_from_db(firestore_db, pid)

@app.get(
    "/orders/{oid}/export_pdf",
    responses={200: {'content': {'application/pdf': {}}}},
    response_class=Response
)
def export_pdf_by_id(oid: str):
    try:
        order = Order.read_from_db(firestore_db, oid)
        order_dict = prepare_order_for_export(order, firestore_db)
    except Exception:
        raise HTTPException(status_code=404, detail='Object not found')
    print(order_dict)
    return Response(content=export_to_pdf(order_dict), media_type='application/pdf')

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
def delete_product(pid: str = Body(..., embed=True)):
    product = Product.read_from_db(firestore_db, pid)
    return product.delete_from_db(firestore_db)

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

@app.post("/move_products_to_inventory")
def move_products_to_inventory(pids: List[str] = Body(..., embed=True)):
    for pid in pids:
        product = Product.read_from_db(firestore_db, pid)
        product.move_to_inventory(firestore_db)
    return "Moved"

@app.post("/mark_order_as_done")
def nark_order_as_done(oid: str = Body(..., embed=True)):
    order = Order.read_from_db(firestore_db, oid)
    return order.move_to_inventory(firestore_db)