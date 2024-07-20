import collections
import json
import math
import struct
import time
import socket

import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage, Qt, QPixmap


class VideoStreamThread(QThread):
    ImageUpdate = Signal(QImage, str)
    NewTargetDetectedSignal = Signal(QPixmap, list, list)
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
        self.saved_detections = []

        self.NewTargetDetectedSignal.connect(parent.parent.parent.targetspage.addTarget)

        # Variables for Hud and Labels
        self.hudcolor = (85, 170, 255)
        self.thickness = 2
        self.p1 = (self.parent.width() // 2 - 200, self.parent.height() // 2)
        self.p2 = (self.parent.width() // 2 + 200, self.parent.height() // 2)

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
        out = cv2.VideoWriter('Database/output.avi', fourcc, 30.0, (640, 480))

        last_detection_length = 0
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

                while len(data) < payload_size:
                    data += connection.recv(4096)
                packed_detection_size = data[:payload_size]
                data = data[payload_size:]
                detection_size = struct.unpack("L", packed_detection_size)[0]

                while len(data) < detection_size:
                    data += connection.recv(4096)
                detection_data = data[:detection_size].decode('utf-8')
                data = data[detection_size:]
                detections = json.loads(detection_data)
                print("Received detections:", detections)

                self.last_data_received_time = current_time

                frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                out.write(frame)  # Video recording
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # If HUD is enabled
                if self.parent.hud_checkbox.isChecked():
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
                    if det not in self.saved_detections:
                        target_frame = frame[det['bb_top']:(det['bb_top'] + det['bb_height'])][det['bb_left']:det['bb_left']+det['bb_width']]
                        target_image = QImage(target_frame.data, target_frame.shape[1], target_frame.shape[0], QImage.Format_RGB888)
                        self.NewTargetDetectedSignal.emit(target_image, [0, 0], [1, 100])
                        self.saved_detections.append(det)

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
        width = self.parent.width() // 2
        height = self.parent.height() // 2
        self.p1 = (int(width - 200 * math.cos(roll)), int(height + 200 * math.sin(roll)))
        self.p2 = (int(width + 200 * math.cos(roll)), int(height - 200 * math.sin(roll)))

    def stop(self):
        self.loop = False
