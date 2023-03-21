from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import pandas as pd

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate(r"C:\Users\tom\Downloads\tom-test-6cfe5-firebase-adminsdk-i9cbg-1c1fe7120c.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def print_db(collection):
    test_col = db.collection(collection).stream()
    return_db = {}
    for col in test_col:
        return_db[col.id] = col.to_dict()
    return return_db

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/show_database", response_class=HTMLResponse)
def get_database():
    df = pd.DataFrame(data=print_db("test"))
    html = df.to_html()
    return """
    <html>
        <head>
            <title>Your Database</title>
        </head>
        <body>
            <h1>Here is your database:</h1>
        """ + html + """
        </body>
    </html
        """