import random
from datetime import datetime, timedelta

from db_handler import DBHandler
from db_structs import Product, Pickup, Order, ProductStatus, OrderStatus

db_handler = DBHandler()


def random_image_url():
    return f"https://picsum.photos/seed/{random.randint(0, 2000)}/500/500"


def create_random_products(num_products: int, is_for_pickup: bool = False):
    products = []
    for i in range(num_products):
        name = f"מוצר {i}"
        description = f"תיאור עבור מוצר {i}"
        image_url = random_image_url()
        # status = random.randint(0, 1)
        status = ProductStatus.COLLECTION if is_for_pickup else ProductStatus.STORAGE
        amount = random.randint(10, 100)
        # reserved = random.randint(0, amount)
        reserved = 0
        origin = f"Origin for product {i}"
        product = Product(name=name, description=description, image_url_list=[image_url],
                          status=status, amount=amount, reserved=reserved, origin=origin)
        products.append(product)
    return products


def insert_random_products(num_products: int, is_for_pickup: bool = False):
    products = create_random_products(num_products=num_products, is_for_pickup=is_for_pickup)
    for product in products:
        did = product.add_to_db(db_handler)
        product.did = did
    return products


def insert_random_pickups(num_pickups: int, num_products_per_pickup: int):
    pickups = []
    for i in range(num_pickups):
        name = f"איסוף {i}"
        address = f"כתובת {i}"
        date = datetime.now() + timedelta(days=random.randint(-10, -1))
        products = insert_random_products(num_products=num_products_per_pickup, is_for_pickup=True)
        products_dids = [product.did for product in products]
        print(products_dids)
        pickup = Pickup(name=name, address=address, date=date, products=products_dids)
        pickups.append(pickup)

    for pickup in pickups:
        did = pickup.add_to_db(db_handler)
        pickup.did = did
    return pickups


def insert_random_orders(num_orders: int, num_products_per_order: int):
    orders = []
    for i in range(num_orders):
        name = f"הזמנה {i}"
        address = f"כתובת {i}"
        description = f"תיאור {i}"
        status = OrderStatus.ORDER_IN_PROGRESS
        date = datetime.now() + timedelta(days=random.randint(-10, -1))
        products = insert_random_products(num_products=num_products_per_order, is_for_pickup=False)
        products_dids = [product.did for product in products]
        print(products_dids)
        order = Order(
            name=name, address=address, description=description, status=status, date=date,
            ordered_products={
                product.did: random.randint(1, 10) for product in products
            }
        )
        orders.append(order)

    for order in orders:
        did = order.add_to_db(db_handler)
        order.did = did
    return orders


def main():
    # insert_random_pickups(num_pickups=2, num_products_per_pickup=2)
    insert_random_orders(num_orders=2, num_products_per_order=2)


if __name__ == '__main__':
    main()
