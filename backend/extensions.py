from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import firebase_admin
from firebase_admin import credentials, db as rtdb

# Created here (not in app.py) so models.py and routes/*.py can import
# `db` and `login_manager` without importing the app factory itself —
# avoids circular imports.
db = SQLAlchemy()
login_manager = LoginManager()

# Firebase Realtime Database initialize
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ecommerce-85772-default-rtdb.asia-southeast1.firebasedatabase.app/'
})