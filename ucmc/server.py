import struct
import cv2
import socket
import threading
import time 
import json

class VideoServer:
    def __init__(self, ip=socket.gethostbyname(socket.gethostname()), port=5050, buffer=1024, shared=None):
        self.buffer = buffer
        self.header = 64
        self.format = 'utf-8'
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((ip, port))
        self.timeout_seconds = 5
        self.shared=shared
        print("[STARTING] server is starting...")
        print(f"[LISTENING] Server is listening on {ip}")

    def start_server(self):
        self.socket.listen()
        while True:
            client_socket, addr = self.socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    def handle_client(self, client_socket, addr):
        print(f"[NEW CONNECTION] {addr} connected.")
        time.sleep(5)
        while True:
            detections,frame,last_update=self.shared.get_detections()
            
            if last_update and time.time() - last_update > self.timeout_seconds:
                print("Detections stream has stopped.")
                data_to_send = json.dumps({"error": "Detections stream has stopped."}).encode()
                client_socket.sendall(data_to_send)
                break
            
            
            detec_data = json.dumps(detections).encode()
            detec_data_length = struct.pack("L", len(detec_data)) 

            text = "ahmed!"  # Example text message
            _, encoded_frame = cv2.imencode('.jpg', frame)
            data = encoded_frame.tobytes()

            message = text.encode(self.format)
            msg_length = len(message)
            send_length = struct.pack("L", msg_length)
            message_size = struct.pack("L", len(data))
            client_socket.sendall(send_length + message + message_size + data + detec_data_length + detec_data)

class sharing:
    def __init__(self):
        self.detections = None
        self.frame=None
        self.last_update_time=None

    def update_detections(self,new_detections,new_frame):
        self.detections = new_detections
        self.frame = new_frame
        self.last_update_time=time.time()

    def get_detections(self):
        return self.detections, self.frame, self.last_update_time




if __name__ == "__main__":
    shared=sharing()
    server = VideoServer(shared=shared)
    
