import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import cv2
import base64
import json
import time
import numpy as np
import os

class HumanPublisher(Node):
    def __init__(self):
        super().__init__('human_publisher_node')
        self.publisher_ = self.create_publisher(String, '/detections', 10)
        timer_period = 5.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.target_id = 1
        
        # Check if dummy image exists
        image_path = "Database/data/deneme/1.jpg"
        if os.path.exists(image_path):
            self.dummy_image = cv2.imread(image_path)
            self.get_logger().info(f"Loaded existing image from {image_path}")
        else:
            # Create a blank image with text if not found
            self.get_logger().info("Dummy image not found, generating a blank one.")
            self.dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
            self.dummy_image.fill(255)
            cv2.putText(self.dummy_image, "Human", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    def timer_callback(self):
        # Encode image to JPEG, then to Base64
        success, buffer = cv2.imencode('.jpg', self.dummy_image)
        if not success:
            self.get_logger().error("Failed to encode image")
            return
            
        img_b64 = base64.b64encode(buffer.tobytes()).decode('utf-8')
        
        # Create JSON payload
        # Dummy coordinates starting roughly around Istanbul
        lat = 41.0 + (self.target_id * 0.005)
        lon = 29.0 + (self.target_id * 0.005)
        
        payload = {
            "id": self.target_id,
            "image": img_b64,
            "location": [lat, lon],
            "first_seen": time.time()
        }
        
        msg = String()
        msg.data = json.dumps(payload)
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing Human ID: {self.target_id} at location: [{lat:.4f}, {lon:.4f}]')
        
        self.target_id += 1

def main(args=None):
    rclpy.init(args=args)
    human_publisher = HumanPublisher()
    
    print("Starting human publisher... Press Ctrl+C to stop.")
    try:
        rclpy.spin(human_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        human_publisher.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
