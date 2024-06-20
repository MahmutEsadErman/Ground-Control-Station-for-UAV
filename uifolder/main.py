import sys

from PySide6 import QtWidgets
from PySide6.QtCore import QThread, Signal

from IndicatorsPage import IndicatorsPage

class IndicatorsThread(QThread):
    update_speed = Signal(int)

    def run(self):
        num =0
        while True:
            # num = int(input("enter speed \n"))
            num += 1
            self.update_speed.emit(num)
            self.msleep(1)


app = QtWidgets.QApplication(sys.argv)

window = IndicatorsPage()
window.show()

thread = IndicatorsThread()
thread.update_speed.connect(window.gyrometer)
thread.update_speed.connect(window.setSpeed)
thread.update_speed.connect(window.setVerticalSpeed)
thread.update_speed.connect(window.setHeading)
thread.update_speed.connect(window.setAltitude)
thread.start()

app.exec()

