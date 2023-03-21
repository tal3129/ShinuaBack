import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

ADMIN_CREDENTIALS = r"shinua_private_key.json"
PRODUCT_COLLECTION = "products"
PICKUPS_COLLECTION = "orders"
ORDERS_COLLECTION = "pickups"

class db_handler():
    def __init__():
        _creds = credentials.Certificate(ADMIN_CREDENTIALS)
        firebase_admin.initialize_app(_creds)
        _db = firestore.client()
    
    def get_collection(collection):
        cols = _db.collection(collection).stream()
        all_items = {}
        for col in cols:
            all_items[col.id] = col.to_dict()
        return all_items