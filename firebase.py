import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage
from firebase_admin import db

cred = credentials.Certificate(r"assets/fir-demo-31f2b-firebase-adminsdk-75i4b-a17ad191f3.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://fir-demo-31f2b-default-rtdb.firebaseio.com/',

})

# assets/ilkdeneme-5656-firebase-adminsdk-10hg3-741e03da89.json
# 'storageBucket': 'gs://ilkdeneme-5656.appspot.com'
# 'databaseURL': 'https://ilkdeneme-5656-default-rtdb.europe-west1.firebasedatabase.app/'

# canberk firebase
#  assets/fir-demo-31f2b-firebase-adminsdk-75i4b-a17ad191f3.json
# 'databaseURL': 'https://fir-demo-31f2b-default-rtdb.firebaseio.com/'

# db = firestore.client()
# coords = db.collection(u'coordinates').document(u'e7rcnNJZtc0xDMaIQ0Nw')

ref = db.reference()
print("eski veri: ")
print(ref.get())

data = {
    'X': 2,
    'Y': 4,
}
# ref.push(data)
ref.child('coordinates').push(data)

print("yeni veri: ")
print(ref.get())
