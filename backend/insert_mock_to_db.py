import json
import random
from datetime import datetime, timedelta

from db_handler import DBHandler
from db_structs import Product, Pickup, Order, ProductStatus, OrderStatus, PRODUCT_COLLECTION, PICKUPS_COLLECTION, \
    ORDERS_COLLECTION

db_handler = DBHandler()
random_products_names_and_descriptions = json.load(open("random_products_heb.json", "rb"))


def random_image_urls(amount: int):
    """
    Return a list of random image urls
    :param amount: number of urls to return
    :return: list of urls
    """
    urls = []
    for _ in range(amount):
        urls.append(f"https://picsum.photos/seed/{random.randint(0, 2000)}/500/500")
    return urls


def random_product_name_and_description():
    """
    Name and description for a random product in Hebrew
    :return:
    """
    return random.choice(random_products_names_and_descriptions)


def create_random_products(num_products: int, is_for_pickup: bool = False):
    products = []
    for i in range(num_products):
        random_product = random_product_name_and_description()
        name = random_product["name"]
        description = random_product["description"]
        image_urls = random_image_urls(amount=3)
        # status = random.randint(0, 1)
        status = ProductStatus.COLLECTION if is_for_pickup else ProductStatus.STORAGE
        amount = random.randint(10, 100)
        # reserved = random.randint(0, amount)
        reserved = 0
        origin = f"Origin for product {i}"
        product = Product(name=name, description=description, image_url_list=image_urls,
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

        did = order.add_to_db(db_handler)
        order.did = did
        orders.append(order)

        for product in products:
            product.recalculate_reserved(db_handler)

    return orders


def reset_db():
    db_handler.delete_everything_in_collection(collection=PRODUCT_COLLECTION)
    db_handler.delete_everything_in_collection(collection=PICKUPS_COLLECTION)
    db_handler.delete_everything_in_collection(collection=ORDERS_COLLECTION)


def main():
    insert_random_pickups(num_pickups=1, num_products_per_pickup=5)
    # insert_random_orders(num_orders=2, num_products_per_order=2)


if __name__ == '__main__':
    main()
