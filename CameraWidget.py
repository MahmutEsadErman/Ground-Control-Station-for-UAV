import math
import sys
import collections
import time
import struct
import socket
import numpy as np
import cv2
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import QApplication, QPushButton, QWidget, QLabel, QVBoxLayout, QSizePolicy, QCheckBox


class CameraWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Create Layout
        self.QVBLayout = QVBoxLayout()
        self.QVBLayout.setContentsMargins(0, 0, 0, 0)  # Set the layout margins
        self.setLayout(self.QVBLayout)  # Set the layout for the widget

        # Create Video Thread
        self.videothread = VideoStreamThread(self)
        self.videothread.ImageUpdate.connect(self.ImageUpdateSlot)

        # Add Label
        self.FeedLabel = QLabel()
        self.FeedLabel.setMinimumSize(640, 480)
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
        print("Connecting to video stream...")
        self.videothread.setIp("127.0.1.1")
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

class VideoStreamThread(QThread):
    ImageUpdate = Signal(QImage, str)
    DISCONNECT_MESSAGE = "!DISCONNECT"

    def __init__(self, parent=None, ip=socket.gethostbyname(socket.gethostname()), port=5050):
        super().__init__()
        self.parent = parent
        self.ip = ip
        self.port = port
        self.header = 64
        self.format = 'utf-8'
        self.timeout_duration = 5
        self.last_data_received_time = 0
        self.loop = True

        # Variables for Hud and Labels
        self.hudcolor = (85, 170, 255)
        self.thickness = 2
        self.p1 = (self.parent.width()//2-200, self.parent.height()//2)
        self.p2 = (self.parent.width()//2+200, self.parent.height()//2)

    def run(self):
        # Connect to the server
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.connect((self.ip, self.port))
            print("Connected to the server.")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return

        # Variables for video stream
        data = b""
        payload_size = struct.calcsize("L")
        prev_frame_time = 0
        font = cv2.FONT_HERSHEY_SIMPLEX
        filter_length = 10
        fps_filter = collections.deque(maxlen=filter_length)

        self.last_data_received_time = time.time()
        self.loop = True

        # Video recording
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # video codec
        out = cv2.VideoWriter('output.avi', fourcc, 30.0, (640, 480))
        # Loop to receive video stream
        while self.loop:
            current_time = time.time()

            if current_time - self.last_data_received_time > self.timeout_duration:
                print(f"No data received for {self.timeout_duration} seconds. Disconnecting...")
                break
            try:
                while len(data) < payload_size:
                    data += connection.recv(4096)
                packed_msg_length = data[:payload_size]
                data = data[payload_size:]
                msg_length = struct.unpack("L", packed_msg_length)[0]

                while len(data) < msg_length:
                    data += connection.recv(4096)
                message = data[:msg_length].decode(self.format)
                data = data[msg_length:]

                while len(data) < payload_size:
                    data += connection.recv(4096)
                packed_message_size = data[:payload_size]
                data = data[payload_size:]
                message_size = struct.unpack("L", packed_message_size)[0]

                while len(data) < message_size:
                    data += connection.recv(4096)
                frame_data = data[:message_size]
                data = data[message_size:]

                self.last_data_received_time = current_time

                frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                out.write(frame)  # Video recording
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


                # if self.parent.hud_checkbox.isChecked():
                # Put FPS
                new_frame_time = time.time()
                fps = 1 / (new_frame_time - prev_frame_time)
                prev_frame_time = new_frame_time
                fps_filter.append(fps)
                avg_fps = sum(fps_filter) / len(fps_filter)
                avg_fps = str(int(avg_fps))
                cv2.putText(frame, avg_fps, (10, 40), font, 1.5, self.hudcolor, self.thickness, cv2.LINE_AA)

                # Put Horizon Line
                cv2.line(frame, self.p1, self.p2, self.hudcolor, self.thickness)


                # Convert frame to QImage
                ConvertToQtFormat = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
                image = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.ImageUpdate.emit(image, message)
            except Exception as e:
                print(f"Error during video stream: {e}")
                break

    def setIp(self, ip):
        self.ip = ip
        print(f"IP address set to {ip}")

    def setHorizon(self, roll):
        width = self.parent.width()//2
        height = self.parent.height()//2
        self.p1 = (int(width-200*math.cos(roll)), int(height+200*math.sin(roll)))
        self.p2 = (int(width+200*math.cos(roll)), int(height-200*math.sin(roll)))

    def stop(self):
        self.loop = False

if __name__ == "__main__":
    app = QApplication([])
    window = CameraWidget()
    window.show()
    sys.exit(app.exec())
