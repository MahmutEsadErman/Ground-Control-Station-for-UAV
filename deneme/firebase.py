import sqlite3
import os

import firebase_admin
from firebase_admin import credentials, db, storage


class Firebase:
    def __init__(self):
        cred = credentials.Certificate(r"uifolder/assets/fir-demo-31f2b-firebase-adminsdk-75i4b-a17ad191f3.json")

        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://fir-demo-31f2b-default-rtdb.firebaseio.com/',
            'storageBucket': 'fir-demo-31f2b.appspot.com'
        })
        self.ref = db.reference("/Users")
        self.users = self.ref.get()

        self.bucket = storage.bucket()

    def add_user_to_database(self, name, image, activity, coordinates):
        # Connect to the SQLite database
        conn = sqlite3.connect('../Database/data/users.db')
        c = conn.cursor()

        # Create the table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     image TEXT NOT NULL,
                     activity INTEGER,
                     x INTEGER,
                     y INTEGER)''')

        # Insert a new user into the database
        c.execute('''INSERT INTO users (name, image, activity, x, y)
                     VALUES (?, ?, ?, ?, ?)''', (name, image, activity, coordinates['x'], coordinates['y']))

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

    def download_image_from_storage(self, image_path_in_storage, destination_folder):
        # Download the image from Firebase Storage
        blob = self.bucket.blob(image_path_in_storage)
        blob.download_to_filename(destination_folder)

    def upload_image_to_storage(self, path_of_image):
        blob = self.bucket.blob("3.jpg")
        blob.upload_from_filename(path_of_image)


fb = Firebase()

# fb.upload_image_to_storage("data/3.jpg")
# fb.download_image_from_storage("1.jpg","1.jpg")
