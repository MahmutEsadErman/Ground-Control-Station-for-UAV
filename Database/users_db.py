import firebase_admin
from PySide6.QtGui import QPixmap
from firebase_admin import credentials
from firebase_admin import db


class FirebaseUser:
    def __init__(self):
        # Initialize the Firebase Admin SDK
        cred = credentials.Certificate(
            'uifolder/assets/ilkdeneme-5656-firebase-adminsdk-10hg3-741e03da89.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://ilkdeneme-5656-default-rtdb.europe-west1.firebasedatabase.app/'
        })

        self.ref = db.reference(f'')

        self.mission = self.get_mission()

        self.users = []
        for i in range(1, 4):
            self.user_ref = db.reference(f'Users/{i}')
            user = {"name": self.get_name(),
                    "authority": self.get_authority(),
                    "image": QPixmap(f"Database/data/{i}.jpg"),
                    "location": [self.get_latitude(), self.get_longitude()],
                    "online": self.get_online()}
            self.users.append(user)

    # Getters
    def get_authority(self):
        return self.user_ref.child('Authority').get()

    def get_image(self):
        return self.user_ref.child('Image').get()

    def get_name(self):
        return self.user_ref.child('Name').get()

    def get_online(self):
        return self.user_ref.child('Online').get()

    def get_latitude(self):
        return self.user_ref.child('Position/latitude').get()

    def get_longitude(self):
        return self.user_ref.child('Position/longitude').get()

    def get_marker_latitude(self):
        return self.ref.child('MarkerLocation/latitude').get()

    def get_marker_longitude(self):
        return self.ref.child('MarkerLocation/longitude').get()

    def get_mission(self):
        return self.ref.child('Mission').get()

    ## Updaters
    def update_authority(self, value):
        self.user_ref.update({'Authority': value})

    def update_image(self, value):
        self.user_ref.update({'Image': value})

    def update_name(self, value):
        self.user_ref.update({'Name': value})

    def update_online(self, value):
        self.user_ref.update({'Online': value})

    def update_latitude(self, value):
        self.user_ref.child('Position').update({'latitude': value})

    def update_longitude(self, value):
        self.user_ref.child('Position').update({'longitude': value})

    def update_marker_latitude(self, value):
        self.ref.child('MarkerLocation').update({'latitude': value})

    def update_marker_longitude(self, value):
        self.ref.child('MarkerLocation').update({'longitude': value})

    def update_mission(self, value):
        self.ref.update({'Mission': value})


if __name__ == '__main__':
    pass
