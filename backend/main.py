"""
This file handles all the routes (relevant to backend)
Should only route requests from frontend and communicate with backend logic to return PYDANTIC objects
"""

from fastapi import FastAPI, Body, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List

from backend.frontend_structs import OrderResponse, OrderedProduct
from export_to_pdf import prepare_order_for_export, export_to_pdf
from backend.db_structs import Product, Order, Pickup
from backend.db_handler import DBHandler, get_all_products, get_all_orders, get_all_pickups

app = FastAPI()
firestore_db = DBHandler()

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


@app.get("/orders")
def get_orders() -> List[OrderResponse]:
    response = []
    orders = get_all_orders(firestore_db)['Orders']
    for order in orders:
        keys = order["ordered_products"].keys()
        ordered_products_response = []
        for pid in keys:
            product = Product.read_from_db(firestore_db, pid)
            ordered_products_response.append(OrderedProduct(
                product=product,
                amount=order["ordered_products"][pid]
            ))
        response.append(OrderResponse(
            did=order["did"],
            name=order["name"],
            address=order["address"],
            description=order["description"],
            date=order["date"],
            ordered_products=ordered_products_response,
            status=order["status"])
        )
    return response

@app.get("/orders/{oid}")
def get_order(oid: str):
    order = Order.read_from_db(firestore_db, oid)
    if order is None:
        raise HTTPException(status_code=400, detail='Order not found')
    keys = order.ordered_products.keys()
    ordered_products_response = []
    for pid in keys:
        product = Product.read_from_db(firestore_db, pid)
        ordered_products_response.append(OrderedProduct(
            product=product,
            amount=order.ordered_products[pid]
        ))
    return OrderResponse(
        did=order.did,
        name=order.name,
        address=order.address,
        description=order.description,
        date=order.date,
        ordered_products=ordered_products_response,
        status=order.status
    )

@app.get("/pickups")
def get_pickups():
    pickups = get_all_pickups(firestore_db)['Pickups']
    for p in pickups:
        res = []
        for pid in p["products"]:
            res.append(Product.read_from_db(firestore_db, pid).dict())
        p["products"] = res
    return pickups

@app.get("/products/{pid}")
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

@app.post("/products/{pid}")
def edit_product(pid: str, product: Product):
    if pid != product.did:
        raise HTTPException(status_code=400, detail='Product id cannot be changed')

    old_product = Product.read_from_db(firestore_db, pid)
    if old_product is None:
        raise HTTPException(status_code=400, detail='Product not found')

    product.recalculate_reserved(db_handler=firestore_db)
    return product.update_to_db(firestore_db)

@app.put("/orders/{oid}")
def edit_order(oid: str, order: Order):
    # Check if one of the ordered product has changed and recalculate the reserved amount properly
    if oid != order.did:
        raise HTTPException(status_code=400, detail='Order id cannot be changed')
    
    old_order = Order.read_from_db(firestore_db, oid)
    if old_order is None:
        raise HTTPException(status_code=400, detail='Order not found')

    order.update_to_db(firestore_db)

    for pid in order.ordered_products.keys():
        if pid in old_order.ordered_products.keys() and order.ordered_products[pid] != old_order.ordered_products[pid]:
            product = Product.read_from_db(firestore_db, pid)
            product.recalculate_reserved(db_handler=firestore_db)
            product.update_to_db(firestore_db)

    for pid in old_order.ordered_products.keys():
        if pid not in order.ordered_products.keys():
            product = Product.read_from_db(firestore_db, pid)
            product.recalculate_reserved(db_handler=firestore_db)
            product.update_to_db(firestore_db)


@app.post("/pickups/{pickup_id}")
def edit_pickup(pickup_id: str, pickup: Pickup):
    if pickup_id != pickup.did:
        raise HTTPException(status_code=400, detail='Pickup id cannot be changed')

    old_pickup = Pickup.read_from_db(firestore_db, pickup_id)
    if old_pickup is None:
        raise HTTPException(status_code=400, detail='Pickup not found')
    return pickup.update_to_db(firestore_db)

# DATA ADDERS

@app.post("/add_product")
def add_product(Product: Product):
    return Product.add_to_db(firestore_db)

@app.post("/add_pickup")
def add_pickup(Pickup: Pickup):
    return Pickup.add_to_db(firestore_db)

@app.post("/orders")
def add_order(Order: Order):
    return Order.add_to_db(firestore_db)

@app.post("/add_product_to_order")
def add_product_to_order(pid: str = Body(...),
                         oid: str = Body(...),
                         amount: int = Body(...)):
    order = Order.read_from_db(firestore_db, oid)
    return order.add_product(firestore_db, pid, amount)

# DATA DELETORS

@app.delete("/products/{pid}")
def delete_product(pid: str):
    product = Product.read_from_db(firestore_db, pid)
    return product.delete_from_db(firestore_db)

@app.delete("/pickups/{did}")
def delete_pickup(did: str):
    pickup = Pickup.read_from_db(firestore_db, did)
    return pickup.delete_from_db(firestore_db)

@app.delete("/orders/{oid}")
def delete_order(oid: str):
    order = Order.read_from_db(firestore_db, oid)
    return order.delete_from_db(firestore_db)

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
    return order.mark_as_done(firestore_db)
