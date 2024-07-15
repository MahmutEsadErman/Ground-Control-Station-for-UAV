import time

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QPushButton, QWidget
from Database.users_db import FirebaseUser as fb


def addUser(parent, user, i):
    parent.addUser(user, i)


class FirebaseStart(QThread):
    create_signal = Signal(QWidget, dict, int)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.firebase = fb()
        self.users = self.firebase.users
        self.number_of_users = 3

        self.create_signal.connect(addUser)

    def run(self):
        for i, user in enumerate(self.users):
            i = i + 1
            self.create_signal.emit(self.parent, user, i)


class FirebaseThread(QThread):
    connectionLost_signal = Signal(QPushButton)

    def __init__(self, firebase, parent=None):
        super().__init__()
        self.parent = parent
        self.loop = True
        self.firebase = firebase
        # self.connectionLost_signal.connect(connectionLost)

    def run(self):
        while self.loop:
            self.msleep(100)



"""  
Başlarken yapılacaklar:
1) Firebase bağlantısı başlatılacak
2) Kaç user olduğu alınacak
3) User bilgileri target page e yansıtılacak

"""
