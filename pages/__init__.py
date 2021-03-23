import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("pages/help-me-shop-2c19d-4640ea944d85.json")
app = firebase_admin.initialize_app(cred)