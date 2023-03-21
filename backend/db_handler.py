import google
import firebase_admin
from firebase_admin import credentials, firestore
from db_structs import PRODUCT_COLLECTION, PICKUPS_COLLECTION, ORDERS_COLLECTION

ADMIN_CREDENTIALS = r"shinua_private_key.json"

# TODO: consider do try and catch on all DB functions
class db_handler():
    def __init__(self):
        self._creds = credentials.Certificate(ADMIN_CREDENTIALS)
        firebase_admin.initialize_app(self._creds)
        self.db = firestore.client()
    
    def get_collection(self, collection):
        return self.db.collection(collection)

    def get_collection_dict(self, collection):
        cols = self.get_collection(collection).stream()
        all_items = []
        for col in cols:
            item = {"did": col.id}
            item.update(col.to_dict())
            all_items.append(item)
        return {f"{collection}": all_items}

    def get_document(self, collection, document_id):
        return self.get_collection(collection).document(document_id).get().to_dict()

    def add_document(self, collection, values_dict):
        return self.get_collection(collection).add(values_dict)

    def set_document(self, collection, document_id, values_dict):
        # Make sure document exists
        if self.get_collection(collection).document(document_id).get().exists:
            try:
                if type(self.get_collection(collection).document(document_id).set(values_dict, merge=False)) is google.cloud.firestore_v1.types.write.WriteResult:
                    return 0
                return 1
            except Exception as x:
                return str(x)
            
        else:
            return "The object you were trying to edit doesnt exists!"

    def delete_document(self, collection, document_id):
        return self.get_collection(collection).document(document_id).delete()

def get_all_products(db_handler):
    return db_handler.get_collection_dict(PRODUCT_COLLECTION)

def get_all_pickups(db_handler):
    return db_handler.get_collection_dict(PICKUPS_COLLECTION)

def get_all_orders(db_handler):
    return db_handler.get_collection_dict(ORDERS_COLLECTION)
