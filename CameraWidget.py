import sys
import time

import cv2
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import QApplication, QPushButton, QWidget, QLabel, QVBoxLayout, QSizePolicy


class CameraWidget(QWidget):
    marker_coord = None

    def __init__(self):
        super().__init__()

        # Create Layout
        self.QVBLayout = QVBoxLayout()

        # Create Video Thread
        self.videothread = VideoThread()
        self.videothread.ImageUpdate.connect(self.ImageUpdateSlot)

        # Add Label
        self.FeedLabel = QLabel()
        self.FeedLabel.setStyleSheet("border: 1px solid black;;")
        self.FeedLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Set size policy
        self.FeedLabel.setScaledContents(True)  # Enable scaling of contents
        self.QVBLayout.addWidget(self.FeedLabel)

        # A variable that holds if the feed is on or off
        self.on_off = False

        # Add buttons
        self.btn_start_cancel = QPushButton("Start")
        self.btn_start_cancel.clicked.connect(self.StartCancelFeed)
        self.QVBLayout.addWidget(self.btn_start_cancel)
        self.setLayout(self.QVBLayout)

        # Allocate Widget Button
        self.btn_AllocateWidget = QPushButton(icon=QIcon("uifolder/assets/icons/16x16/cil-arrow-top.png"), parent=self)
        self.btn_AllocateWidget.setCursor(Qt.PointingHandCursor)
        self.btn_AllocateWidget.setStyleSheet("background-color: rgb(44, 49, 60);")
        self.btn_AllocateWidget.resize(25, 25)

        # A variable that holds if the widget is child of the main window or not
        self.isAttached = True

    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def StartCancelFeed(self):
        if self.on_off:
            self.videothread.stop()
            self.videothread.finished.connect(lambda: self.FeedLabel.clear())
            self.btn_start_cancel.setText("Start")
            self.on_off = False
        else:
            self.startingTime = time.time_ns() / 1000
            self.videothread.start()
            self.btn_start_cancel.setText("Cancel")
            self.on_off = True

    def resizeEvent(self, event):
        self.btn_AllocateWidget.move(self.width() - self.btn_AllocateWidget.width(), 0)
        super().resizeEvent(event)


class VideoThread(QThread):
    ImageUpdate = Signal(QImage)

    def __init__(self):
        super().__init__()
        self.ThreadActive = True

    def run(self):
        capture = cv2.VideoCapture(0)
        self.ThreadActive = True
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # video codec
        out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))
        while self.ThreadActive:
            ret, frame = capture.read()
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                FlippedImage = cv2.flip(Image, 1)
                cv2.putText(FlippedImage, str(capture.get(cv2.CAP_PROP_FPS)), (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (15,160,60), 2)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                out.write(frame) # Video recording
                self.ImageUpdate.emit(Pic)

    def stop(self):
        self.ThreadActive = False
        self.quit()


if __name__ == "__main__":
    app = QApplication([])
    window = CameraWidget()
    window.show()
    sys.exit(app.exec())
