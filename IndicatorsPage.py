import math
import sys
import time

from PySide6.QtCore import Qt, QPropertyAnimation, QPoint, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QApplication, QPushButton

from uifolder import Ui_IndicatorsPage


class IndicatorsPage(QWidget, Ui_IndicatorsPage):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Indicators' values
        self.maxSpeed = 33
        self.maxVerticalSpeed = 12

        # frame width: 296, height: 272
        # Animation Duration
        self.duration = 200

        # Add buttons
        self.btn_AllocateWidget = QPushButton(icon=QIcon("uifolder/assets/icons/16x16/cil-arrow-top.png"), parent=self)
        self.btn_AllocateWidget.setCursor(Qt.PointingHandCursor)
        self.btn_AllocateWidget.setStyleSheet("background-color: rgb(44, 49, 60);")
        self.btn_AllocateWidget.resize(25, 25)

        # A variable that holds if the widget is child of the main window or not
        self.isAttached = True

    def rotate_needle(self, angle, needle):
        # Calculate the shortest path for the rotation
        current_angle = needle.getAngle()
        if abs(angle - current_angle) > 180:
            # Adjust angles for minimal rotation distance
            if angle < current_angle:
                angle += 360
            else:
                current_angle += 360

        # Set up the animation
        rotation_animation = QPropertyAnimation(needle, b"angle", parent=self)
        rotation_animation.setStartValue(current_angle)
        rotation_animation.setEndValue(angle)
        rotation_animation.setDuration(self.duration)
        rotation_animation.start()

    def setAttitude(self, pitch, roll):
        pitch = pitch*2 - 2
        move_animation = QPropertyAnimation(self.attitude_middle, b"pos", parent=self)
        move_animation.setEndValue(QPoint(self.attitude_middle.x(), 43+pitch))
        move_animation.setDuration(300)
        move_animation.start()
        self.rotate_needle(roll, self.attitude_middle)
        self.attitude_text.setText(pitch)

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

        move_animation = QPropertyAnimation(self.altitude_needle, b"pos", parent=self)
        move_animation.setEndValue(QPoint(self.altitude_needle.x(), altitude))
        move_animation.setDuration(500)
        move_animation.start()


    def resizeEvent(self, event):
        self.btn_AllocateWidget.move(self.width() - self.btn_AllocateWidget.width(), 0)
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IndicatorsPage()
    window.show()
    sys.exit(app.exec())
