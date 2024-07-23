import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QPushButton, QWidget, QLabel, QVBoxLayout, QCheckBox, QDialog, QInputDialog

from Database.VideoStream import VideoStreamThread


class CameraWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        # Create Layout
        self.QVBLayout = QVBoxLayout()
        self.QVBLayout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins
        self.setLayout(self.QVBLayout)  # Set the layout for the widget

        # Create Video Thread
        self.videothread = VideoStreamThread(self)
        self.videothread.ImageUpdate.connect(self.ImageUpdateSlot)

        # Add Label
        self.FeedLabel = QLabel()
        # self.FeedLabel.setMinimumSize(640, 480)
        self.FeedLabel.setScaledContents(True)  # Enable scaling of contents
        self.QVBLayout.addWidget(self.FeedLabel)

        # Add buttons
        self.connect_button = QPushButton("Connect", parent=self)
        self.connect_button.setCursor(Qt.PointingHandCursor)
        self.connect_button.clicked.connect(self.connectStream)

        self.disconnect_button = QPushButton("X", parent=self)
        self.disconnect_button.setCursor(Qt.PointingHandCursor)
        self.disconnect_button.clicked.connect(self.disconnect)
        self.disconnect_button.resize(25, 25)
        self.disconnect_button.hide()

        self.labels_checkbox = QCheckBox(parent=self, styleSheet="background-color: transparent;color: blue;")
        self.hud_checkbox = QCheckBox(parent=self, styleSheet="background-color: transparent;color: blue;")

        # Allocate Widget Button
        self.btn_AllocateWidget = QPushButton(icon=QIcon("uifolder/assets/icons/16x16/cil-arrow-top.png"), parent=self)
        self.btn_AllocateWidget.setCursor(Qt.PointingHandCursor)
        self.btn_AllocateWidget.setStyleSheet("background-color: rgb(44, 49, 60);")
        self.btn_AllocateWidget.resize(25, 25)

        self.videothread.finished.connect(self.handleFinish)

        # A variable that holds if the widget is child of the main window or not
        self.isAttached = True

    def ImageUpdateSlot(self, image, message):
        self.FeedLabel.setPixmap(QPixmap.fromImage(image))
        self.message = message

    def handleFinish(self):
        blank_pixmap = QPixmap(640, 480)
        blank_pixmap.fill(Qt.gray)
        self.FeedLabel.setPixmap(blank_pixmap)
        self.disconnect_button.hide()
        self.connect_button.show()

    def connectStream(self):
        ip, okPressed = QInputDialog.getText(self, "Enter IP Address", "IP Address:", text="192.168.1.1")
        if okPressed:
            print("Connecting to video stream...")
            self.videothread.setIp(ip)
            self.videothread.start()
            self.connect_button.hide()
            self.disconnect_button.show()

    def disconnect(self):
        self.videothread.stop()

    def resizeEvent(self, event):
        self.btn_AllocateWidget.move(self.width() - self.btn_AllocateWidget.width(), 0)
        self.connect_button.move(int((self.width() - self.connect_button.width()) / 2), int((self.height() - self.connect_button.height()) / 2))
        self.labels_checkbox.move(50+self.disconnect_button.width() , 0)
        self.hud_checkbox.move(50+self.disconnect_button.width()*2 , 0)
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    window = CameraWidget()
    window.show()
    sys.exit(app.exec())
