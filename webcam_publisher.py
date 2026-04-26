import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class WebcamPublisher(Node):
    def __init__(self):
        super().__init__('webcam_publisher_node')
        # Create publisher for the camera/image topic
        self.publisher_ = self.create_publisher(Image, 'camera/image', 10)
        # We will publish 30 times a second
        timer_period = 1.0 / 30.0  
        self.timer = self.create_timer(timer_period, self.timer_callback)
        # Open the default webcam
        self.cap = cv2.VideoCapture(0)
        self.bridge = CvBridge()
        self.get_logger().info('Webcam publisher node has started.')

    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert OpenCV image to ROS 2 Image message
            msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            self.publisher_.publish(msg)
        else:
            self.get_logger().warning('Failed to capture frame from webcam')

def main(args=None):
    rclpy.init(args=args)
    webcam_publisher = WebcamPublisher()
    
    try:
        rclpy.spin(webcam_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up resources
        webcam_publisher.cap.release()
        webcam_publisher.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
