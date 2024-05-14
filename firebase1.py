import sqlite3
import os

import firebase_admin
from firebase_admin import credentials, db, storage


class firebase_db:
    def __init__(self):
        cred = credentials.Certificate(r"uifolder/assets/fir-demo-31f2b-firebase-adminsdk-75i4b-a17ad191f3.json")

        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://fir-demo-31f2b-default-rtdb.firebaseio.com/',
        })
        self.ref = db.reference("/Users")
        self.users = self.ref.get()

    def add_user_to_database(self, name, image, activity, coordinates):
        # Connect to the SQLite database
        conn = sqlite3.connect('data/users.db')
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

    # # Example usage:
    # user_name = "John Doe"
    # user_image = "profile_pic.jpg"
    # user_activity = True
    # user_coordinates = {'x': 10, 'y': 20}
    #
    # add_user_to_database(user_name, user_image, user_activity, user_coordinates)


class firebase_st:
    def __init__(self):
        cred = credentials.Certificate(r"uifolder/assets/fir-demo-31f2b-firebase-adminsdk-75i4b-a17ad191f3.json")
        name = "storageBucket"
        app = firebase_admin.initialize_app(cred, {
            'storageBucket': 'gs://fir-demo-31f2b.appspot.com/', },
                                             name)

        self.bucket = storage.bucket( "profileImgs",app = app)

    def download_image_from_firebase_storage(self, image_path_in_storage, destination_folder):
        # Download the image from Firebase Storage
        blob = self.bucket.blob(image_path_in_storage)
        blob.download_to_filename(destination_folder)


dbase = firebase_db()
st = firebase_st()
for user in dbase.users:
    print(user)
    if user is not None:
        st.download_image_from_firebase_storage("siyahprofilfoto.jpg", "data/image.jpg")
