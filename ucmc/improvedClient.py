import collections
import time
import struct
import cv2
import socket
import threading
import json
import numpy as np

class VideoClient:
    def __init__(self, ip=socket.gethostbyname(socket.gethostname()), port=5050):
        self.header = 64
        self.format = 'utf-8'
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        threading.Thread(target=self.get_stream).start()

    def get_stream(self):
        data = b""
        payload_size = struct.calcsize("L")
        prev_frame_time = 0
        font = cv2.FONT_HERSHEY_SIMPLEX
        filter_length = 10
        fps_filter = collections.deque(maxlen=filter_length)

        while True:
            while len(data) < payload_size:
                data += self.socket.recv(4096)
            packed_msg_length = data[:payload_size]
            data = data[payload_size:]
            msg_length = struct.unpack("L", packed_msg_length)[0]

            while len(data) < msg_length:
                data += self.socket.recv(4096)
            message = data[:msg_length].decode(self.format)
            data = data[msg_length:]

            while len(data) < payload_size:
                data += self.socket.recv(4096)
            packed_message_size = data[:payload_size]
            data = data[payload_size:]
            message_size = struct.unpack("L", packed_message_size)[0]

            while len(data) < message_size:
                data += self.socket.recv(4096)
            frame_data = data[:message_size]
            data = data[message_size:]

            while len(data) < payload_size:
                data += self.socket.recv(4096)
            packed_detection_size = data[:payload_size]
            data = data[payload_size:]
            detection_size = struct.unpack("L", packed_detection_size)[0]

            while len(data) < detection_size:
                data += self.socket.recv(4096)
            detection_data = data[:detection_size].decode('utf-8')
            data = data[detection_size:]
            detections=json.loads(detection_data)
            print("Received detections:", detections)

            frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            new_frame_time = time.time()
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time
            fps_filter.append(fps)
            avg_fps = sum(fps_filter) / len(fps_filter)
            avg_fps = str(int(avg_fps))

            for det in detections:
                if det['track_id'] > 0:
                    cv2.rectangle(frame, (int(det['bb_left']), int(det['bb_top'])), (int(det['bb_left']+det['bb_width']), int(det['bb_top']+det['bb_height'])), (0, 255, 0), 2)
                    cv2.putText(frame, str(det['track_id']), (int(det['bb_left']), int(det['bb_top'])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


            cv2.putText(frame, avg_fps, (10, 40), font, 1.5, (100, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, message, (10, 80), font, 1.5, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.imshow('stream', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

if __name__ == "__main__":
    client = VideoClient("127.0.1.1")
