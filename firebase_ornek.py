import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage
from firebase_admin import db

cred = credentials.Certificate(r"uifolder/assets/fir-demo-31f2b-firebase-adminsdk-75i4b-a17ad191f3.json")

app = firebase_admin.initialize_app(cred, {
    # 'storageBucket': 'gs://fir-demo-31f2b.appspot.com/',
    'databaseURL': 'https://fir-demo-31f2b-default-rtdb.firebaseio.com/',
})

ref = db.reference()
# buc = storage.bucket(app=app)

print("eski veri: ")
print(ref.get())

data = {
    'ID': 1,
    'Name': "ahmet",
    "pos": {"x": 1, "y" : 2},
}
data2 = {"x": 5, "y" : 6}

# file = f"uifolder/assets/plane.png"

# blob = buc.blob("my_blob")
# blob.upload_from_string('hello world')

# ref.push(data),
# ref.child('Users').child('pos').update(data2)

print("yeni veri: ")
print(ref.get())
