import sys

from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QLabel, QApplication, QPushButton

from PIL import Image
from PIL.ImageQt import ImageQt

from uifolder import Ui_IndicatorsPage


class IndicatorsPage(QWidget, Ui_IndicatorsPage):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Load images
        self.needle_image = Image.open(u"uifolder/assets/needle.png")
        self.needle_gs_image = Image.open(u"uifolder/assets/needle_gs.png")
        self.needle_plane_image = Image.open(u"uifolder/assets/plane.png")

        # Indicators' values
        self.maxSpeed = 22
        self.maxVerticalSpeed = 12

        # frame width: 296, height: 272

        # Add buttons
        self.btn_AllocateWidget = QPushButton(icon=QIcon("uifolder/assets/icons/16x16/cil-arrow-top.png"), parent=self)
        self.btn_AllocateWidget.setCursor(Qt.PointingHandCursor)
        self.btn_AllocateWidget.setStyleSheet("background-color: rgb(44, 49, 60);")
        self.btn_AllocateWidget.resize(25, 25)

        # A variable that holds if the widget is child of the main window or not
        self.isAttached = True

    def rotate_needle(self, angle, needle: QLabel):
        if needle == self.gyro_needle:
            image = self.needle_gs_image
        elif needle == self.direction_needle:
            image = self.needle_plane_image
        else:
            image = self.needle_image
        rotated_needle = QtGui.QPixmap.fromImage(ImageQt(image.rotate(-int(angle))))
        needle.setPixmap(rotated_needle)

    def gyrometer(self, degree):
        self.rotate_needle(degree, self.gyro_needle)

    def setSpeed(self, speed):
        if speed < self.maxSpeed:
            degree = speed * 360 / self.maxSpeed
        else:
            degree = 360

        degree = 280 / 360 * degree + 140
        self.rotate_needle(degree, self.speed_needle)
        self.speed_text.setText("%.2f" % speed)

    def setVerticalSpeed(self, speed):
        if self.maxVerticalSpeed > speed > -self.maxVerticalSpeed:
            degree = speed * 180 / self.maxVerticalSpeed + 180
        else:
            degree = 0

        self.rotate_needle(degree, self.vspeed_needle)
        self.speed_text_2.setText("%.2f" % speed)

    def setHeading(self, degree):
        self.rotate_needle(degree, self.direction_needle)

    def setAltitude(self, altitude):
        if altitude < 0:
            altitude = 0
        elif altitude > 120:
            altitude = -altitude
        altitude = -500 / 126 * altitude + 510
        self.altitude_needle.setGeometry(self.altitude_needle.x(), altitude, self.altitude_needle.width(),
                                         self.altitude_needle.height())

    def resizeEvent(self, event):
        self.btn_AllocateWidget.move(self.width() - self.btn_AllocateWidget.width(), 0)
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IndicatorsPage()
    window.show()
    sys.exit(app.exec())
