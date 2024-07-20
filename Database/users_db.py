import concurrent.futures

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


class FirebaseUser:
    def __init__(self):
        # Initialize the Firebase Admin SDK
        cred = credentials.Certificate(
            'Database/ilkdeneme-5656-firebase-adminsdk-10hg3-741e03da89.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://ilkdeneme-5656-default-rtdb.europe-west1.firebasedatabase.app/'
        })
        #
        # cred = credentials.Certificate(
        #     'Database/fir-demo-31f2b-firebase-adminsdk-75i4b-a17ad191f3.json')
        # firebase_admin.initialize_app(cred, {
        #     'databaseURL': 'https://fir-demo-31f2b-default-rtdb.firebasedatabase.app/'
        # })

        self.ref = db.reference(f'')

        self.mission = self.get_mission()

        self.users = []

        self.user_number = 4

        self.init_users()

    def init_users(self):
        for i in range(0, self.user_number):
            user = {"name": self.get_name(i),
                    "authority": self.get_authority(i),
                    "image": f"Database/data/{i}.jpg",
                    "location": [self.get_latitude(i), self.get_longitude(i)],
                    "online": self.get_online(i)}
            self.users.append(user)

    def updateUsers(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.update_user_data, i) for i in range(self.user_number)]
            concurrent.futures.wait(futures)

    def update_user_data(self):
        for i in range(0, self.user_number):
            self.users[i]["location"] = [self.get_latitude(i), self.get_longitude(i)]
            self.users[i]["online"] = self.get_online(i)

    # Getters
    def get_authority(self, id):
        self.user_ref = db.reference(f'Users/{id}')
        return self.user_ref.child('Authority').get()

    def get_image(self, id):
        self.user_ref = db.reference(f'Users/{id}')
        return self.user_ref.child('Image').get()

    def get_name(self, id):
        self.user_ref = db.reference(f'Users/{id}')
        return self.user_ref.child('Name').get()

    def get_online(self, id):
        self.user_ref = db.reference(f'Users/{id}')
        return self.user_ref.child('Online').get()

    def get_latitude(self, id):
        self.user_ref = db.reference(f'Users/{id}')
        return self.user_ref.child('Position/latitude').get()

    def get_longitude(self, id):
        self.user_ref = db.reference(f'Users/{id}')
        return self.user_ref.child('Position/longitude').get()

    def get_marker_latitude(self):
        return self.ref.child('MarkerLocation/latitude').get()

    def get_marker_longitude(self):
        return self.ref.child('MarkerLocation/longitude').get()

    def get_mission(self):
        return self.ref.child('Mission').get()

    ## Updaters
    def update_authority(self, value, id):
        self.user_ref = db.reference(f'Users/{id}')
        self.user_ref.update({'Authority': value})

    def update_image(self, value, id):
        self.user_ref = db.reference(f'Users/{id}')
        self.user_ref.update({'Image': value})

    def update_name(self, value, id):
        self.user_ref = db.reference(f'Users/{id}')
        self.user_ref.update({'Name': value})

    def update_online(self, value, id):
        self.user_ref = db.reference(f'Users/{id}')
        self.user_ref.update({'Online': value})

    def update_latitude(self, value, id):
        self.user_ref = db.reference(f'Users/{id}')
        self.user_ref.child('Position').update({'latitude': value})

    def update_longitude(self, value, id):
        self.user_ref = db.reference(f'Users/{id}')
        self.user_ref.child('Position').update({'longitude': value})

    def update_marker_latitude(self, value):
        self.ref.child('MarkerLocation').update({'latitude': value})

    def update_marker_longitude(self, value):
        self.ref.child('MarkerLocation').update({'longitude': value})

    def update_mission(self, value):
        self.ref.update({'Mission': value})


if __name__ == '__main__':
    pass
