import sys
from PySide6.QtWidgets import QApplication

from Database.Cloud import FirebaseThread
from MainWindow import MainWindow
from Database.users_db import FirebaseUser

if __name__ == '__main__':

    try:
        firebase = FirebaseUser()
        # Firebase Thread
        firebaseThread = FirebaseThread(firebase)
        firebaseThread.start()
    except:
        firebase = None
        pass

    app = QApplication(sys.argv)
    window = MainWindow(firebase)
    window.show()
    sys.exit(app.exec())
