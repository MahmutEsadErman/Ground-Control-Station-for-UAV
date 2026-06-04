import time
import json
import base64

import cv2
import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from sensor_msgs.msg import CompressedImage
from vision_msgs.msg import Detection2DArray
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

        self.bridge = CvBridge()
        self.node = None
        self.topic = '/camera/image'

    def run(self):
        self.context = Context()
        rclpy.init(context=self.context)

        self.node = rclpy.create_node('gcs_video_stream_node', context=self.context)
        self.subscription = self.node.create_subscription(
            CompressedImage,
            self.topic,
            self.image_callback,
            10)

        self.detection_subscription = self.node.create_subscription(
            Detection2DArray,
            '/detections',
            self.detection_callback,
            10)

        self.starting_time = time.time()
        print(f"Video stream node started, waiting for ROS 2 images on {self.topic}...")

        self.executor = SingleThreadedExecutor(context=self.context)
        self.executor.add_node(self.node)

        try:
            self.executor.spin()
        except Exception as e:
            print(f"Exception in Video Stream ROS 2 node thread: {e}")
        finally:
            self.executor.remove_node(self.node)
            if self.node:
                self.node.destroy_node()
            if hasattr(self, 'context') and self.context.ok():
                rclpy.shutdown(context=self.context)

    def image_callback(self, msg):
        try:
            frame = self.bridge.compressed_imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            print(f"Failed to convert image: {e}")
            return

        self.latest_frame = frame.copy()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert frame to QImage
        ConvertToQtFormat = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        image = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ImageUpdate.emit(image, "ROS2 Image")

    def detection_callback(self, msg):
        try:
            for det in msg.detections:
                target_id = int(det.id) if det.id else 0
                location = [0.0, 0.0]
                first_seen = time.time()

                # Calculate bounding box
                x = det.bbox.center.position.x
                y = det.bbox.center.position.y
                w = det.bbox.size_x
                h = det.bbox.size_y
                
                x1 = max(0, int(x - w / 2))
                y1 = max(0, int(y - h / 2))
                x2 = int(x + w / 2)
                y2 = int(y + h / 2)

                frame = None
                if hasattr(self, 'latest_frame') and self.latest_frame is not None:
                    h_frame, w_frame, _ = self.latest_frame.shape
                    x1 = min(x1, w_frame)
                    x2 = min(x2, w_frame)
                    y1 = min(y1, h_frame)
                    y2 = min(y2, h_frame)
                    
                    if x2 > x1 and y2 > y1:
                        frame = self.latest_frame[y1:y2, x1:x2].copy()

                if frame is not None:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    ConvertToQtFormat = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
                    qimage = ConvertToQtFormat.copy()  # Deep copy is required to keep data alive

                    # Emit signal (start and end time are same initially)
                    self.NewTargetDetectedSignal.emit(qimage, location, [first_seen, first_seen], target_id)
                else:
                    print("Could not crop image from the latest frame.")

        except Exception as e:
            print(f"Error parsing detection msg: {e}")

    def setTopic(self, topic):
        self.topic = topic

    def stop(self):
        if hasattr(self, 'context') and self.context.ok():
            # We don't call exit inside since rclpy.spin is blocking. We can shutdown the node context.
            self.context.try_shutdown()
        self.quit()

    def sendMessage(self, msg):
        pass
