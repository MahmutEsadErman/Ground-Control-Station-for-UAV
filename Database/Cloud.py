from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QWidget
from Database.users_db import FirebaseUser


class FirebaseThread(QThread):
    updateFirebase_signal = Signal()

    def __init__(self, user_id, firebase, parent=None):
        super().__init__()
        self.parent = parent
        self.id = user_id
        self.loop = True
        self.firebase = firebase
        self.updateFirebase_signal.connect(self.firebase.updateUsers)

    def run(self):
        while self.loop:
            self.updateFirebase_signal.emit()
            self.msleep(1000)

    def stop(self):
        self.loop = False


def updateUserMenu(usermenu, firebase, id):
    if usermenu.isOnline != firebase.users[id]['online']:
        usermenu.setOnline(firebase.users[id]['online'])
    if usermenu.location_label.text()[10:] != str(firebase.users[id]['location']):
        usermenu.setLocation(firebase.users[id]['location'])


class UpdateUserMenuThread(QThread):
    updateUserMenu_signal = Signal(QWidget, FirebaseUser, int)

    def __init__(self, user_id, firebase, usermenu, parent=None):
        super().__init__()
        self.parent = parent
        self.id = user_id
        self.loop = True
        self.firebase = firebase
        self.usermenu = usermenu
        self.updateUserMenu_signal.connect(updateUserMenu)

    def run(self):
        while self.loop:
            self.updateUserMenu_signal.emit(self.usermenu, self.firebase, self.id)
            self.msleep(200)

    def stop(self):
        self.loop = False
