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
from std_msgs.msg import String
from cv_bridge import CvBridge

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage, Qt
from PySide6.QtWidgets import QWidget

class VideoStreamThread(QThread):
    ImageUpdate = Signal(QImage, str)
    NewTargetDetectedSignal = Signal(QImage, list, list, int)
    UpdateTargetSignal = Signal(int, list, QImage)

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
        self.UpdateTargetSignal.connect(parent.parent.parent.targetspage.updateTarget)

        self.bridge = CvBridge()
        self.node = None
        self.topic = '/camera/camera/color/image_raw/compressed'
        self.known_targets = set()

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
            String,
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
            try:
                payload = json.loads(msg.data)
            except json.JSONDecodeError:
                import ast
                payload = ast.literal_eval(msg.data)
                
            target_id = payload.get("id", 0)
            print(f"Target ID: {target_id}")
            location = payload.get("location", [41.27442, 28.727317])
            if isinstance(location, str):
                import ast
                location = ast.literal_eval(location)
                
            first_seen = payload.get("first_seen", time.time())
            
            img_b64 = payload.get("image", "")
            qimage = QImage()
            if img_b64:
                # Clean and pad base64 string
                img_b64 = img_b64.strip()
                if "base64," in img_b64:
                    img_b64 = img_b64.split("base64,")[1]
                pad = 4 - (len(img_b64) % 4)
                if pad < 4:
                    img_b64 += "=" * pad
                    
                img_bytes = base64.b64decode(img_b64)
                np_arr = np.frombuffer(img_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if frame is not None:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    ConvertToQtFormat = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
                    qimage = ConvertToQtFormat.copy()
                else:
                    print("Warning: cv2.imdecode returned None for detection image")

            if target_id not in self.known_targets:
                self.known_targets.add(target_id)
                if not qimage.isNull():
                    self.NewTargetDetectedSignal.emit(qimage, location, [first_seen, first_seen], target_id)
            else:
                # Target already exists, emit update signal with new image
                print(f"Target {target_id} already known. Emitting UpdateTargetSignal...")
                self.UpdateTargetSignal.emit(target_id, location, qimage)

        except Exception as e:
            print(f"Error parsing JSON detection msg: {e}")

    def setTopic(self, topic):
        self.topic = topic

    def stop(self):
        if hasattr(self, 'context') and self.context.ok():
            # We don't call exit inside since rclpy.spin is blocking. We can shutdown the node context.
            self.context.try_shutdown()
        self.quit()

    def sendMessage(self, msg):
        pass
