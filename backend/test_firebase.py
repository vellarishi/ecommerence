import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ecommerce-85772-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

ref = db.reference('/')
ref.set({'backend_test': 'connection working from python'})
print("✅ Data written successfully!")