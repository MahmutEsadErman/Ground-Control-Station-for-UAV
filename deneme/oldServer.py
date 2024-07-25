import collections
import time
import struct
import cv2
import socket
import threading

class VideoServer:
    def __init__(self, ip=socket.gethostbyname(socket.gethostname()), port=5050, buffer=1024):
        self.buffer = buffer
        self.header = 64
        self.format = 'utf-8'
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cap = cv2.VideoCapture(0)
        self.socket.bind((ip, port))
        print("[STARTING] server is starting...")
        print(f"[LISTENING] Server is listening on {ip}")
        self.start_server()

    def start_server(self):
        self.socket.listen()
        while True:
            client_socket, addr = self.socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    def handle_client(self, client_socket, addr):
        print(f"[NEW CONNECTION] {addr} connected.")
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            text = "Hello from server!"  # Example text message
            _, encoded_frame = cv2.imencode('.jpg', frame)
            data = encoded_frame.tobytes()

            message = text.encode(self.format)
            msg_length = len(message)
            send_length = struct.pack("L", msg_length)
            message_size = struct.pack("L", len(data))
            client_socket.sendall(send_length + message + message_size + data)

if __name__ == "__main__":
    server = VideoServer()
