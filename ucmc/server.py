import struct
import cv2
import socket
import threading
import time 
import msgpack

class HandleMessageThread(threading.Thread):

    def __init__(self, client_socket):
        super().__init__()
        self.buffer = 1024
        self.header = 64
        self.format = 'utf-8'
        self.client_socket = client_socket

    def run(self):
        #Receiving Message
        while True:
            print("receive")
            data=b""
            payload_size = struct.calcsize("L")
            while len(data) < payload_size:
                data += self.client_socket.recv(4096)
            packed_msg_length = data[:payload_size]
            data = data[payload_size:]
            msg_length = struct.unpack("L", packed_msg_length)[0]

            while len(data) < msg_length:
                data += self.client_socket.recv(4096)
            message = data[:msg_length].decode(self.format)
            data = data[msg_length:]
            
            print('New Message:', message)

class VideoServerThread(threading.Thread):
    def __init__(self, ip=socket.gethostbyname(socket.gethostname()), port=5050, buffer=1024, shared=None):
        super().__init__()
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

    def run(self):
        frame_time=1/self.shared.fps
        self.socket.listen()
        
        client_socket, addr = self.socket.accept()
        print(f"[NEW CONNECTION] {addr} connected.")
        handle_message_thread = HandleMessageThread(client_socket)
        handle_message_thread.start()
        while True:
            start_time=time.time()
            print('send')
            detections,frame,last_update=self.shared.get_detections()
            
            if last_update and time.time() - last_update > self.timeout_seconds:
                print("Detections stream has stopped.")
                data_to_send = msgpack.packb({"error": "Detections stream has stopped."})
                client_socket.sendall(data_to_send)
                break
            
            
            detec_data = msgpack.packb(detections)
            detec_data_length = struct.pack("L", len(detec_data)) 

            text = "ahmed!"  # Example text message
            _, encoded_frame = cv2.imencode('.jpg', frame)
            data = encoded_frame.tobytes()

            message = text.encode(self.format)
            msg_length = len(message)
            send_length = struct.pack("L", msg_length)
            message_size = struct.pack("L", len(data))

            elapsed_time= time.time() -start_time
            sleep_time=  frame_time - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)
            client_socket.sendall(send_length + message + message_size + data + detec_data_length + detec_data)
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")




class sharing:
    def __init__(self,fps):
        self.detections = None
        self.frame=None
        self.last_update_time=None
        self.fps=fps
    def update_detections(self,new_detections,new_frame):
        self.detections = new_detections
        self.frame = new_frame
        self.last_update_time=time.time()

    def get_detections(self):
        return self.detections, self.frame, self.last_update_time

if __name__ == "__main__":
    shared=sharing()
    server = VideoServerThread(shared=shared)
    
