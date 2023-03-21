import firebase_admin
from firebase_admin import credentials, firestore

ADMIN_CREDENTIALS = r"shinua_private_key.json"


class db_handler():
    def __init__(self):
        self._creds = credentials.Certificate(ADMIN_CREDENTIALS)
        firebase_admin.initialize_app(self._creds)
        self.db = firestore.client()
    
    def get_collection(self, collection):
        return self.db.collection(collection)

    def get_collection_dict(self):
        self.get_collection().stream()
        all_items = {}
        for col in cols:
            all_items[col.id] = col.to_dict()
        return all_items

    def get_document(self, collection, document_id):
        did = document_id if isinstance(document_id, str) else str(document_id)
        return self.get_collection(collection).document(did).get().to_dict()

    def add_document(self, collection, values_dict):
        return self.get_collection(collection).add(values_dict)

    def set_document(self, collection, document_id, values_dict):
        did = document_id if isinstance(document_id, str) else str(document_id)
        return self.get_collection(collection).document(did).set(values_dict, merge=False)

def get_all_products():
    return firestore_db.get_collection(PRODUCT_COLLECTION)

def get_all_pickups():
    return firestore_db.get_collection(PICKUPS_COLLECTION)

def get_all_orders():
    return firestore_db.get_collection(ORDERS_COLLECTION)

def get_product_by_id(pid):
    pass

