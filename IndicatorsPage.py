import sys

from PySide6 import QtGui
from PySide6.QtWidgets import QWidget, QLabel, QApplication

from PIL import Image
from PIL.ImageQt import ImageQt

from uifolder import Ui_IndicatorsPage

class IndicatorsPage(QWidget, Ui_IndicatorsPage):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Testing
        self.needle_image = Image.open(u"uifolder/assets/needle.png")
        self.needle_gs_image = Image.open(u"uifolder/assets/Needle_gs.png")
        self.needle_plane_image = Image.open(u"uifolder/assets/Plane.png")


        # self.needle_image = Image.open(u"../assets/needle.png")
        # self.needle_gs_image = Image.open(u"../assets/Needle_gs.png")
        # self.needle_plane_image = Image.open(u"../assets/Plane.png")


        # Indicators' values
        self.maxSpeed = 22
        self.maxVerticalSpeed = 12

        # frame width: 296, height: 272

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
            degree = speed*360/self.maxSpeed
        else:
            degree = 360

        degree = 280 / 360 * degree + 125
        self.rotate_needle(degree, self.speed_needle)

    def setVerticalSpeed(self, speed):
        if self.maxVerticalSpeed > speed > -self.maxVerticalSpeed:
            degree = speed*180/self.maxVerticalSpeed + 180
        else:
            degree = 0

        self.rotate_needle(degree, self.vspeed_needle)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IndicatorsPage()
    window.show()
    sys.exit(app.exec())
