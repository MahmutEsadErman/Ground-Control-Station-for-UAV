import firebase_admin
from firebase_admin import credentials, db, storage


class FirebaseUser:
    def __init__(self):
        # Initialize the Firebase Admin SDK
        # cred = credentials.Certificate(
        #     'Database/ilkdeneme-5656-firebase-adminsdk-10hg3-741e03da89.json')
        # firebase_admin.initialize_app(cred, {
        #     'databaseURL': 'https://ilkdeneme-5656-default-rtdb.europe-west1.firebasedatabase.app/'
        # })

        cred = credentials.Certificate(
            'Database/fir-demo-31f2b-firebase-adminsdk-75i4b-a17ad191f3.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://fir-demo-31f2b-default-rtdb.us-central1.firebasedatabase.app/'
            # , 'storageBucket': 'fir-demo-31f2b.appspot.com'
        })

        self.ref = db.reference(f'')
        self.user_ref = db.reference(f'Users')
        # self.blob = storage.bucket()

        self.users = []
        self.targets = []

        self.user_number = 3

        # UAV marker informations
        self.marker_latitude = 0
        self.marker_longitude = 0
        self.marker_compass = 0

        self.update_mission(0)
        self.init_users()
        self.init_targets()


    def init_users(self):
        for i in range(1, self.user_number+1):
            user = {"name": self.get_name(i),
                    "authority": self.get_authority(i),
                    "image": f"Database/data/{i}.jpg",
                    "location": [self.get_latitude(i), self.get_longitude(i)],
                    "online": self.get_online(i)}
            self.users.append(user)

    def init_targets(self):
        self.ref.update({'Targets': ""})

    def send_targets(self):
        for target in self.targets:
            self.update_target(target["id"], target["visibility"], target["latitude"], target["longitude"],
                               target["image"])

    def update_target(self, id, visibility, latitude, longitude, image):
        self.update_target_visibility(visibility, id)
        self.update_target_latitude(latitude, id)
        self.update_target_longitude(longitude, id)
        self.update_target_image(image, id)

    def get_user_data(self):
        for i in range(self.user_number):
            self.users[i]["location"] = [self.get_latitude(i+1), self.get_longitude(i+1)]
            self.users[i]["online"] = self.get_online(i+1)

    def update_marker_data(self, compass, longitude, latitude):
        self.update_marker_compass(compass)
        self.update_marker_longitude(longitude)
        self.update_marker_latitude(latitude)

    ####################################################################################################################
    ## Getters
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

    def get_marker_compass(self):
        return self.ref.child('Marker/compass').get()

    def get_marker_latitude(self):
        return self.ref.child('Marker/latitude').get()

    def get_marker_longitude(self):
        return self.ref.child('Marker/longitude').get()

    def get_mission(self):
        return self.ref.child('Mission').get()

    ####################################################################################################################

    ## Updaters
    def update_target_visibility(self, value, id):
        self.user_ref = db.reference(f'Targets/{id}')
        self.user_ref.update({'in_view': value})

    def update_target_image(self, filename, id):
        # self.blob = self.blob.blob(f"videoImages/{id}")
        # self.blob.upload_from_string(filename)
        self.user_ref = db.reference(f'Targets/{id}')
        self.user_ref.update({'image': filename})

    def update_target_latitude(self, value, id):
        self.user_ref = db.reference(f'Targets/{id}')
        self.user_ref.update({'latitude': value})

    def update_target_longitude(self, value, id):
        self.user_ref = db.reference(f'Targets/{id}')
        self.user_ref.update({'longitude': value})

    def update_user_authority(self, value, id):
        self.user_ref = db.reference(f'Users/{id}')
        self.user_ref.update({'Authority': value})

    def update_user_image(self, value, id):
        self.user_ref = db.reference(f'Users/{id}')
        self.user_ref.update({'Image': value})

    def update_user_name(self, value, id):
        self.user_ref = db.reference(f'Users/{id}')
        self.user_ref.update({'Name': value})

    def update_user_online(self, value, id):
        self.user_ref = db.reference(f'Users/{id}')
        self.user_ref.update({'Online': value})

    def update_user_latitude(self, value, id):
        self.user_ref = db.reference(f'Users/{id}')
        self.user_ref.child('Position').update({'latitude': value})

    def update_user_longitude(self, value, id):
        self.user_ref = db.reference(f'Users/{id}')
        self.user_ref.child('Position').update({'longitude': value})

    def update_marker_compass(self):
        self.ref.child('Marker').update({'compass': self.marker_compass})

    def update_marker_latitude(self):
        self.ref.child('Marker').update({'latitude': self.marker_latitude})

    def update_marker_longitude(self):
        self.ref.child('Marker').update({'longitude': self.marker_longitude})

    def update_marker_heading(self, value):
        self.ref.child('MarkerLocation').update({'compass': value})

    def update_mission(self, value):
        self.ref.update({'Mission': value})


if __name__ == '__main__':
    pass
