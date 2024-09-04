import collections
import math
import struct
import time
import socket
import msgpack

import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage, Qt
from PySide6.QtWidgets import QWidget

from math import asin, atan2, cos, degrees, radians, sin


def updateTargetPosition(mainwindow, no, position):
    mainwindow.homepage.mapwidget.page().runJavaScript(f"target_marker{no}.setLatLng({str(position)});")
    mainwindow.targetspage.setLeavingTime(no, time.time() * 1000)


class VideoStreamThread(QThread):
    ImageUpdate = Signal(QImage, str)
    NewTargetDetectedSignal = Signal(QImage, list, float, int)
    UpdateTargetPositionSignal = Signal(QWidget, int, list)
    DISCONNECT_MESSAGE = "!DISCONNECT"

    def __init__(self, parent=None, ip=socket.gethostbyname(socket.gethostname()), port=5050):
        super().__init__()
        self.parent = parent
        self.ip = ip
        self.port = port
        self.header = 64
        self.format = 'utf-8'
        self.timeout_duration = 2
        self.last_data_received_time = 0
        self.loop = True
        self.saved_detections = {}
        self.starting_time = 0
        # Variables for target position
        self.lat = 0
        self.lon = 0
        self.heading = 0

        self.NewTargetDetectedSignal.connect(parent.parent.parent.targetspage.addTarget)
        self.UpdateTargetPositionSignal.connect(updateTargetPosition)

        # Variables for Hud and Labels
        self.hudcolor = (85, 170, 255)
        self.thickness = 2
        self.p1 = (self.parent.width() // 2 - 200, self.parent.height() // 2)
        self.p2 = (self.parent.width() // 2 + 200, self.parent.height() // 2)

    def run(self):
        # Connect to the server
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.settimeout(self.timeout_duration)
            self.connection.connect((self.ip, self.port))
            print("Connected to the server.")
            self.starting_time = time.time()
            # # Set TCP_NODELAY to True to disable Nagle's algorithm
            # self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            #
            # # Increase buffer sizes
            # self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)  # Send buffer
            # self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2048)  # Receive buffer

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

        self.loop = True

        # Video recording
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # video codec
        width = 960
        height = 540
        out = cv2.VideoWriter('Database/output.avi', fourcc, 30.0, (width, height))

        # Loop to receive video stream
        while self.loop:
            try:
                print("Receiving video stream...")
                self.last_data_received_time = time.time()

                # Read the message length
                while len(data) < payload_size:
                    data += self.connection.recv(4096)
                packed_msg_length = data[:payload_size]
                data = data[payload_size:]
                msg_length = struct.unpack("L", packed_msg_length)[0]

                # Read the message
                while len(data) < msg_length:
                    data += self.connection.recv(4096)
                message = data[:msg_length].decode(self.format)
                data = data[msg_length:]

                # Read the frame length
                while len(data) < payload_size:
                    data += self.connection.recv(4096)
                packed_message_size = data[:payload_size]
                data = data[payload_size:]
                message_size = struct.unpack("L", packed_message_size)[0]

                # Read the frame data
                while len(data) < message_size:
                    data += self.connection.recv(4096)
                frame_data = data[:message_size]
                data = data[message_size:]

                # Read the detection size
                while len(data) < payload_size:
                    data += self.connection.recv(4096)
                packed_detection_size = data[:payload_size]
                data = data[payload_size:]
                detection_size = struct.unpack("L", packed_detection_size)[0]

                # Read the detection data
                while len(data) < detection_size:
                    data += self.connection.recv(4096)
                detection_data = data[:detection_size]
                data = data[detection_size:]
                detections = msgpack.unpackb(detection_data, raw=False)

                if time.time() - self.last_data_received_time > self.timeout_duration:
                    print("Connection timeout")
                    break

                frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                out.write(frame)  # Video recording
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                raw_frame = np.copy(frame)

                # If HUD is enabled
                if self.parent.hud_checkbox.isChecked():
                    # Put FPS
                    new_frame_time = time.time()
                    fps = 1 / (new_frame_time - prev_frame_time)
                    prev_frame_time = new_frame_time
                    fps_filter.append(fps)
                    avg_fps = sum(fps_filter) / len(fps_filter)
                    avg_fps = str(int(avg_fps))
                    cv2.putText(frame, avg_fps, (40, 60), font, 1.5, self.hudcolor, self.thickness, cv2.LINE_AA)
                    # Put Horizon Line
                    cv2.line(frame, self.p1, self.p2, self.hudcolor, self.thickness)

                # If Labeling is enabled
                if self.parent.labels_checkbox.isChecked():
                    for det in detections:
                        if det['track_id'] > 0:
                            cv2.rectangle(frame, (int(det['bb_left']), int(det['bb_top'])), (
                                int(det['bb_left'] + det['bb_width']), int(det['bb_top'] + det['bb_height'])),
                                          (0, 255, 0),
                                          2)
                            cv2.putText(frame, str(det['track_id']), (int(det['bb_left']), int(det['bb_top'])),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                for det in detections:
                    position = self.get_point_at_distance(0)
                    if det['track_id'] not in self.saved_detections:
                        print(f"New target detected: {det['track_id']}")
                        self.setImageBorders(det)
                        target_image = QImage(raw_frame.data, raw_frame.shape[1], raw_frame.shape[0],
                                              QImage.Format_RGB888)
                        target_image = target_image.copy(det['bb_left'], det['bb_top'], det['bb_width'],
                                                         det['bb_height'])
                        self.NewTargetDetectedSignal.emit(target_image, position, time.time(), det['track_id'])
                        self.saved_detections[det['track_id']] = True

                    self.UpdateTargetPositionSignal.emit(self.parent.parent.parent, det['track_id'], position)

                # Convert frame to QImage
                ConvertToQtFormat = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
                image = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.ImageUpdate.emit(image, message)
            except Exception as e:
                print(f"Error during video stream: {e}")

    def setIp(self, ip):
        self.ip = ip
        print(f"IP address set to {ip}")

    def setHorizon(self, roll):
        width = self.parent.width() // 2
        height = self.parent.height() // 2
        self.p1 = (int(width - 200 * math.cos(roll)), int(height + 200 * math.sin(roll)))
        self.p2 = (int(width + 200 * math.cos(roll)), int(height - 200 * math.sin(roll)))

    def stop(self):
        self.loop = False

    def sendMessage(self, msg):
        message = msg.encode(self.format)
        message_length = len(message)
        send_length = struct.pack("L", message_length)
        self.connection.sendall(send_length + message)

    def setImageBorders(self, detection):
        if detection['bb_width'] > detection['bb_height']:
            detection['bb_width'] = detection['bb_width'] + detection['bb_width']/10
            detection['bb_height'] = detection['bb_width']
            detection['bb_left'] = detection['bb_left'] - detection['bb_width']/10
            detection['bb_top'] = detection['bb_top'] - detection['bb_width']/10
        else:
            detection['bb_height'] = detection['bb_height'] + detection['bb_height']/10
            detection['bb_width'] = detection['bb_height']
            detection['bb_top'] = detection['bb_top'] - detection['bb_height']/10
            detection['bb_left'] = detection['bb_left'] - detection['bb_height']/10

    def get_point_at_distance(self, d, R=6371):
        """
        lat: initial latitude, in degrees
        lon: initial longitude, in degrees
        d: target distance from initial
        bearing: (true) heading in degrees
        R: optional radius of sphere, defaults to mean radius of earth

        Returns new lat/lon coordinate {d}km from initial, in degrees
        """
        lat1 = radians(self.lat)
        lon1 = radians(self.lon)
        a = radians(self.heading)
        lat2 = asin(sin(lat1) * cos(d / R) + cos(lat1) * sin(d / R) * cos(a))
        lon2 = lon1 + atan2(
            sin(a) * sin(d / R) * cos(lat1),
            cos(d / R) - sin(lat1) * sin(lat2)
        )
        return degrees(lat2), degrees(lon2)
