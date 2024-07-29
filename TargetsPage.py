import sys

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout, \
    QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, QEvent, QTimer, QByteArray, QBuffer, QIODevice

from Database.Cloud import UpdateUserMenuThread
from uifolder import Ui_TargetsPage
from MediaPlayer import MediaPlayerWindow
from MapWidget import image_to_base64


def qimage_to_base64(qimage, image_format="PNG"):
    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QIODevice.WriteOnly)
    image = qimage.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    image.save(buffer, image_format)
    base64_data = byte_array.toBase64().data().decode("utf-8")
    return base64_data


class TargetsPage(QWidget, Ui_TargetsPage):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
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
        self.firebase = self.parent.firebase
        if self.firebase != None:
            QTimer.singleShot(3000, self.addUsers)

        # Test
        # self.addTarget(QPixmap("Database/data/1.jpg"), "Location 1", (10, 100))

    def addTarget(self, image, position, time, no):
        # Create a new target
        self.number_of_targets += 1
        self.targets[no] = {"image": image, "location": position, "time_interval": [time*1000, 0]}

        # Create a container widget for the target
        container = self.createContainer(f"target{no}", QPixmap.fromImage(image),
                                         self.number_of_targets)

        # Add the container widget to the grid layout
        self.targetsWidget.layout().addWidget(container, self.row, self.column)

        self.column += 1
        if self.column > 5:  # Adjust this value to change the number of columns
            self.column = 0
            self.row += 1

        # Add target marker
        image_base64 = 'data:image/png;base64,' + qimage_to_base64(image)
        self.parent.homepage.mapwidget.page().runJavaScript(f"""
                    target_marker{no} = L.marker({position}, {{icon: targetIcon}}).addTo(map);
                    target_marker{no}.bindTooltip('<br>' + "<img src='{image_base64}'/>");
                """)

    def setLeavingTime(self, no, time):
        self.targets[no]["time_interval"][1] = time

    def addUsers(self):
        for i, user in enumerate(self.firebase.users):
            container = self.createContainer(f"user{i}", QPixmap(user["image"]), i)
            self.usersWidget.layout().addWidget(container)

            if user["location"] is not None and all(user["location"]):
                # Add user marker
                location = user["location"]
                name = user["name"].replace("'", "\\'")
                image = 'data:image/png;base64,' + image_to_base64(user["image"])
                self.parent.homepage.mapwidget.page().runJavaScript(f"""
                    user_marker{i} = L.marker({location}, {{icon: userIcon}}).addTo(map);
                    user_marker{i}.bindTooltip('{name}' + '<br>' + "<img src='{image}'/>");
                """)
                print(f'User {i} added to the map with location: {location}')
            else:
                print(f'User {i} has invalid location data: {user["location"]}')

        # Update users positions every 100ms
        self.update_users_positions_timer = QTimer()
        self.update_users_positions_timer.timeout.connect(self.update_users_positions)
        self.update_users_positions_timer.start(100)

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

    def update_users_positions(self):
        for i, user in enumerate(self.firebase.users):
            if user["location"] is not None and all(user["location"]):
                # Update user marker
                location = user["location"]
                self.parent.homepage.mapwidget.page().runJavaScript(f"user_marker{i}.setLatLng({location});")
            else:
                print(f'User {i} has invalid location data: {user["location"]}')

    def eventFilter(self, obj, event):
        if obj.objectName()[:-1] == "target":
            # When double clicked open a new window
            if event.type() == QEvent.MouseButtonDblClick:
                no = int(obj.objectName()[-1])
                self.newWindow = MediaPlayerWindow(QPixmap.fromImage(self.targets[no]["image"]),
                                                   self.targets[no]["location"],
                                                   self.targets[no]["time_interval"],
                                                   self.parent.homepage.cameraWidget.videothread.starting_time)
                self.newWindow.show()
        elif obj.objectName()[:-1] == "user":
            if event.type() == QEvent.MouseButtonDblClick:
                no = int(obj.objectName()[-1])
                self.newWindow = UserMenu(no, self.firebase.users[no]["name"],
                                          QPixmap(self.firebase.users[no]["image"]),
                                          self.firebase.users[no]["location"], self)
                self.update_user_menu = UpdateUserMenuThread(no, self.firebase, self.newWindow)
                self.update_user_menu.start()
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

    def giveAuthority(self):
        if self.authority_button.text() == "Yetki Ver":
            self.authority_button.setText("Yetkiyi Geri Al")
            self.parent.firebase.update_authority(False, self.id)
        else:
            self.authority_button.setText("Yetki Ver")
            self.parent.firebase.update_authority(True, self.id)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TargetsPage()
    window.show()
    sys.exit(app.exec())
