import sys

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow, QScrollArea, QLabel, QGridLayout, \
    QPushButton
from PySide6.QtCore import Qt, QEvent

from uifolder import Ui_TargetsPage
from MediaPlayer import MediaPlayerWindow
from users_db import FirebaseUser as firebase


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

        # Users Dictionary
        self.users = firebase().users
        self.number_of_users = 3

        # Test
        self.addTarget(QPixmap("data/1.jpg"), "Location 1", (10, 100))
        self.addTarget(QPixmap("data/2.jpg"), "Location 2", (20, 200))
        self.addTarget(QPixmap("data/3.jpg"), "Location 3", (30, 300))

        self.addUser(1)
        self.addUser(2)
        self.addUser(3)

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

    def addUser(self, id):
        #     # Create a new user
        #     self.number_of_users += 1
        #     self.users[self.number_of_users] = {"pixmap": pixmap, "location": location}
        #
        # Create a container widget for the user
        container = self.createContainer(f"user{self.number_of_users}", self.users[id]["image"], id)

        # Add the container widget to the grid layout
        self.usersWidget.layout().addWidget(container)

    def createContainer(self, name, pixmap, number):
        # Create a QWidget to hold both labels
        container = QWidget(objectName=name)
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
                no = int(obj.objectName()[-1])
                self.newWindow = UserMenu(self.users[no]["image"], "Location")
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
    def __init__(self, pixmap, location):
        # Resim, İsim, Online olma durumu, Konum, yetki verme Buton
        super().__init__()
        self.setMaximumWidth(200)
        self.resize(200, self.height())
        self.setLayout(QVBoxLayout())

        self.isOnline = False

        scaled_pixmap = pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
        image_label = QLabel(pixmap=scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(image_label)

        location_label = QLabel("Location: \n" + str(location))
        location_label.setAlignment(Qt.AlignTop)
        self.layout().addWidget(location_label)

        self.isonline_label = QLabel("Online: \n" + str(self.isOnline))
        self.isonline_label.setAlignment(Qt.AlignTop)
        self.layout().addWidget(self.isonline_label)

        button = QPushButton("Show on Map")
        self.layout().addWidget(button)

    def setOnline(self, online):
        self.isOnline = online
        self.isonline_label.setText("Online: \n" + str(self.isOnline))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TargetsPage()
    window.show()
    sys.exit(app.exec())
