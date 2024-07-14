import time

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QPushButton, QWidget
from Database.users_db import FirebaseUser as fb


def fonksiyon(parent, user, i):
    print("çalışıyor")
    parent.targetspage.addUser(user, i)


class FirebaseStart(QThread):
    create_signal = Signal(QWidget, dict, int)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.users = fb().users
        self.number_of_users = 3

        self.create_signal.connect(fonksiyon)

    def run(self):
        for i, user in enumerate(self.users):
            i = i + 1
            fonksiyon(self.parent, user, i)


class FirebaseThread(QThread):
    connectionLost_signal = Signal(QPushButton)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        # self.connectionLost_signal.connect(connectionLost)

    def run(self):
        pass


"""  
Başlarken yapılacaklar:
1) Firebase bağlantısı başlatılacak
2) Kaç user olduğu alınacak
3) User bilgileri target page e yansıtılacak

"""
