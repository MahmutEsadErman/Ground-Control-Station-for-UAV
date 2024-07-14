from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QPushButton
from Database.users_db import FirebaseUser as fb




class FirebaseStart(QThread):

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.users = fb().users
        self.number_of_users = 3

    def run(self):
        for i in range(1, self.number_of_users):
            self.parent.targetspage.addUser(i, self.number_of_users)

class FirebaseThread(QThread):
    connectionLost_signal = Signal(QPushButton)
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.connectionLost_signal.connect(connectionLost)

    def run(self):
        pass

"""  
Başlarken yapılacaklar:
1) Firebase bağlantısı başlatılacak
2) Kaç user olduğu alınacak
3) User bilgileri target page e yansıtılacak
    

"""
