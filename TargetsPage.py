import sys

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout, \
    QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, QEvent, Signal

from Database.Cloud import FirebaseStart, FirebaseThread
from uifolder import Ui_TargetsPage
from MediaPlayer import MediaPlayerWindow


class TargetsPage(QWidget, Ui_TargetsPage):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Set Layout
        self.setLayout(QVBoxLayout())

        # Set Widget inside Target Scroll Area
        self.targetsWidget = QWidget()
        self.targetsWidget.setLayout(QGridLayout())
        self.targetsWidget.layout().setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.row = 0
        self.column = 0
        self.targets_scrollarea.setWidget(self.targetsWidget)

        # Targets Dictionary
        self.targets = {}
        self.number_of_targets = 0

        # Set Container stylesheet varible
        self.containerStyleSheet = """QWidget:hover{border: 2px solid rgb(64, 71, 88);} QLabel::hover{border: 0px;}"""

        self.oldtarget = QWidget()

        # Set Widget inside Mobile Scroll Area
        self.usersWidget = QWidget()
        self.usersWidget.setLayout(QVBoxLayout())
        self.usersWidget.layout().setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.users_scrollarea.setWidget(self.usersWidget)

        # Firebase Thread
        self.initialize_firebase = FirebaseStart(self)
        self.firebase = self.initialize_firebase.firebase
        self.initialize_firebase.start()

        # Test
        self.addTarget(QPixmap("Database/data/1.jpg"), "Location 1", (10, 100))
        self.addTarget(QPixmap("Database/data/2.jpg"), "Location 2", (20, 200))
        self.addTarget(QPixmap("Database/data/3.jpg"), "Location 3", (30, 300))

    def addTarget(self, pixmap, location, time_interval):
        # Create a new target
        self.number_of_targets += 1
        self.targets[self.number_of_targets] = {"pixmap": pixmap, "location": location, "time_interval": time_interval}

        # Create a container widget for the target
        container = self.createContainer(f"target{self.number_of_targets}", pixmap, self.number_of_targets)

        # Add the container widget to the grid layout
        self.targetsWidget.layout().addWidget(container, self.row, self.column)

        self.column += 1
        if self.column > 4:  # Adjust this value to change the number of columns
            self.column = 0
            self.row += 1

    def addUser(self, user, i):
        container = self.createContainer(f"user{i}", user["image"], i)
        self.usersWidget.layout().addWidget(container)

    def createContainer(self, objectname, pixmap, number):
        # Create a QWidget to hold both labels
        container = QWidget(objectName=objectname)
        layout = QVBoxLayout()
        container.setLayout(layout)
        container.setStyleSheet(self.containerStyleSheet)
        container.setMinimumSize(80, 80)
        container.setMaximumSize(150, 150)

        # Create the image label
        scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
        image_label = QLabel()
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        layout.addWidget(image_label)

        # Create the text label
        text_label = QLabel(str(number))
        text_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        layout.addWidget(text_label)

        # Set click event for container
        container.installEventFilter(self)

        return container

    def eventFilter(self, obj, event):
        if obj.objectName()[:-1] == "target":
            # When double clicked open a new window
            if event.type() == QEvent.MouseButtonDblClick:
                no = int(obj.objectName()[-1])
                self.newWindow = MediaPlayerWindow(self.targets[no]["pixmap"], self.targets[no]["location"],
                                                   self.targets[no]["time_interval"])
                self.newWindow.show()
        elif obj.objectName()[:-1] == "user":
            if event.type() == QEvent.MouseButtonDblClick:
                no = int(obj.objectName()[-1])-1
                self.newWindow = UserMenu(no, self.firebase.users[no]["name"], self.firebase.users[no]["image"], self.firebase.users[no]["location"], self)
                self.firebasethread = FirebaseThread(no, self.firebase, self.newWindow)
                self.firebasethread.start()
                self.newWindow.setCloseSignal(self.firebasethread.stop)
                self.newWindow.show()

        # When clicked change the border color
        if event.type() == QEvent.MouseButtonPress:
            if event.buttons() == Qt.LeftButton:
                self.oldtarget.setStyleSheet(self.containerStyleSheet)
                obj.setStyleSheet("""
                    QWidget{border: 2px solid rgb(64, 71, 88);}
                    QLabel{border: 0px;}
                            """)
                self.oldtarget = obj
                return True

        return super().eventFilter(obj, event)


class UserMenu(QWidget):
    close_signal = Signal()
    def __init__(self, id, name, pixmap, location, parent=None):
        super().__init__()
        self.parent = parent
        self.id = id
        self.setMaximumWidth(200)
        self.resize(200, self.height())
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(10)

        self.isOnline = False

        scaled_pixmap = pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label = QLabel(pixmap=scaled_pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.image_label)

        self.name_label = QLabel(str(name))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.name_label)

        self.location_label = QLabel("Location: \n" + str(location))
        self.location_label.setAlignment(Qt.AlignTop)
        self.layout().addWidget(self.location_label)

        self.isonline_label = QLabel("Online: \n" + str(self.isOnline))
        self.isonline_label.setAlignment(Qt.AlignTop)
        self.layout().addWidget(self.isonline_label)

        self.authority_button = QPushButton("Yetki Ver")
        self.layout().addWidget(self.authority_button)

        self.layout().addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.authority_button.clicked.connect(self.giveAuthority)

    def setOnline(self, online):
        self.isOnline = online
        self.isonline_label.setText("Online: \n" + str(self.isOnline))

    def setLocation(self, location):
        self.location_label.setText("Location: \n" + str(location))

    def setCloseSignal(self, func):
        self.close_signal.connect(func)

    def giveAuthority(self):
        if self.authority_button.text() == "Yetki Ver":
            self.authority_button.setText("Yetkiyi Geri Al")
            self.parent.firebase.update_authority(self.id, False)
        else:
            self.authority_button.setText("Yetki Ver")
            self.parent.firebase.update_authority(self.id, True)

    def closeEvent(self, event):
        self.close_signal.emit()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TargetsPage()
    window.show()
    sys.exit(app.exec())
