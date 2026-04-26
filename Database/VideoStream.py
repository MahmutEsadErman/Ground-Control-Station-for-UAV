import collections
import math
import time

import cv2
import numpy as np

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage, Qt
from PySide6.QtWidgets import QWidget


def updateTargetPosition(mainwindow, no, position):
    mainwindow.homepage.mapwidget.page().runJavaScript(f"target_marker{no}.setLatLng({str(position)});")
    mainwindow.targetspage.setLeavingTime(no, time.time())


class VideoStreamThread(QThread):
    ImageUpdate = Signal(QImage, str)
    NewTargetDetectedSignal = Signal(QImage, list, list, int)
    UpdateTargetPositionSignal = Signal(QWidget, int, list)

    def __init__(self, parent=None, ip=None, port=None):
        super().__init__()
        self.parent = parent
        self.starting_time = 0
        self.loop = True
        
        # Variables for target position
        self.lat = 0
        self.lon = 0
        self.heading = 0

        self.NewTargetDetectedSignal.connect(parent.parent.parent.targetspage.addTarget)
        self.UpdateTargetPositionSignal.connect(updateTargetPosition)

        # Variables for Hud and Labels
        self.hudcolor = (85, 170, 255)
        self.thickness = 2
        self.p1 = (int(self.parent.width() // 6), int(self.parent.height() // 2))
        self.p2 = (int(self.parent.width() - self.parent.width() // 6), int(self.parent.height() // 2))
        
        self.bridge = CvBridge()
        self.node = None
        self.fps_filter = collections.deque(maxlen=10)
        self.prev_frame_time = 0
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.topic = '/camera/image'

    def run(self):
        if not rclpy.ok():
            rclpy.init()

        self.node = rclpy.create_node('gcs_video_stream_node')
        self.subscription = self.node.create_subscription(
            Image,
            self.topic,
            self.image_callback,
            10)

        self.starting_time = time.time()
        print(f"Video stream node started, waiting for ROS 2 images on {self.topic}...")

        try:
            rclpy.spin(self.node)
        except Exception as e:
            print(f"Exception in Video Stream ROS 2 node thread: {e}")
        finally:
            if self.node:
                self.node.destroy_node()

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            print(f"Failed to convert image: {e}")
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        raw_frame = np.copy(frame)

        # If HUD is enabled
        if self.parent.hud_checkbox.isChecked():
            # Put FPS
            new_frame_time = time.time()
            if self.prev_frame_time > 0:
                fps = 1 / (new_frame_time - self.prev_frame_time)
                self.fps_filter.append(fps)
                if len(self.fps_filter) > 0:
                    avg_fps = sum(self.fps_filter) / len(self.fps_filter)
                    cv2.putText(frame, str(int(avg_fps)), (40, 60), self.font, 1.5, self.hudcolor, self.thickness, cv2.LINE_AA)
            self.prev_frame_time = new_frame_time
            # Put Horizon Line
            cv2.line(frame, self.p1, self.p2, self.hudcolor, self.thickness)

        # Convert frame to QImage
        ConvertToQtFormat = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        image = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ImageUpdate.emit(image, "ROS2 Image")

    def setTopic(self, topic):
        self.topic = topic

    def setHorizon(self, roll):
        x = self.parent.width() // 6
        y = self.parent.height() // 2
        length = 2 * self.parent.width() // 3
        self.p1 = (int(x * math.cos(roll)), int(y + length * math.sin(roll)))
        self.p2 = (int(self.parent.width() - x + length * math.cos(roll)), int(y - length * math.sin(roll)))

    def stop(self):
        if self.node:
            # We don't call exit inside since rclpy.spin is blocking. We can shutdown the node context.
            pass
        self.quit()

    def sendMessage(self, msg):
        pass

    def setImageBorders(self, detection):
        pass
