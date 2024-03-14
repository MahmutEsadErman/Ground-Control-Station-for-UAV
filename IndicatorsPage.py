import io

from PySide6 import QtGui
from PySide6.QtCore import Qt, QThread, Signal, QPoint, QBuffer
from PySide6.QtGui import QTransform, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QWidget, QLabel

from PIL import Image
from PIL.ImageQt import ImageQt

from uifolder import Ui_IndicatorsPage


class IndicatorsPage(QWidget, Ui_IndicatorsPage):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Indicators")
        self.needle_image = Image.open(u"assets/needle.png")
        self.needle_gs_image = Image.open(u"assets/Needle_gs.png")
        self.needle_plane_image = Image.open(u"assets/Plane.png")

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

    def speedometer(self, degree):

        if 0 > degree:
            degree = 0

        elif degree > 360:
            degree -= 360

        degree = 280 / 360 * degree + 125
        self.rotate_needle(degree, self.speed_needle)

    def vspeedometer(self, degree):
        if degree < 0:
            degree = 0

        elif degree > 360:
            degree = 360
        degree = 1 / 2 * degree + 180
        self.rotate_needle(degree, self.vspeed_needle)

    def headingmeter(self, degree):
        self.rotate_needle(degree, self.direction_needle)

    def altimeter(self, altitude):

        altitude = 120
        if altitude < 0:
            altitude = 0
        elif altitude > 120:
            altitude = -altitude

        altitude = -500 / 126 * altitude + 510

        print(self.altitude_needle.y())
        self.altitude_needle.setGeometry(self.altitude_needle.x(), altitude, self.altitude_needle.width(),
                                         self.altitude_needle.height())
