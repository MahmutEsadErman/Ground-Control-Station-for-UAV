from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QWidget
from Database.users_db import FirebaseUser as fb, FirebaseUser


def addUser(parent, user, i):
    parent.addUser(user, i)


class FirebaseStart(QThread):
    create_signal = Signal(QWidget, dict, int)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.firebase = fb()

        self.create_signal.connect(addUser)

    def run(self):
        for i, user in enumerate(self.firebase.users):
            i = i + 1
            self.create_signal.emit(self.parent, user, i)


def updateUserMenu(usermenu, firebase, id):
    if usermenu.isOnline != firebase.users[id]['online']:
        usermenu.setOnline(firebase.users[id]['online'])
    if usermenu.location_label.text()[10:] != str(firebase.users[id]['location']):
        usermenu.setLocation(firebase.users[id]['location'])

def updateUsers(firebase):
    firebase.updateUsers()


class FirebaseThread(QThread):
    updateUserMenu_signal = Signal(QWidget, FirebaseUser, int)
    updateFirebase_signal = Signal(FirebaseUser)

    def __init__(self, user_id, firebase, usermenu, parent=None):
        super().__init__()
        self.parent = parent
        self.id = user_id
        self.loop = True
        self.firebase = firebase
        self.usermenu = usermenu
        self.updateUserMenu_signal.connect(updateUserMenu)
        self.updateFirebase_signal.connect(updateUsers)

    def run(self):
        while self.loop:
            self.updateFirebase_signal.emit(self.firebase)
            self.msleep(1000)
            self.updateUserMenu_signal.emit(self.usermenu, self.firebase, self.id)
            self.msleep(1000)

    def stop(self):
        self.loop = False
