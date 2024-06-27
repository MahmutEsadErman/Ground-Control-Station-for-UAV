import struct
import cv2
import socket
import pickle
import threading

HEADER = 64
PORT = 5050
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('10.254.254.254', 1))
print(s.getsockname())
IP = s.getsockname()[0]  # socket.gethostbyname(socket.gethostname())  # local ip , "78.188.55.182" public ip
s.close()
ADDR = (IP, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# Set up camera
cap = cv2.VideoCapture(0)


# while True:
#     ret, frame = cap.read()
#     ret, buffer = cv2.imencode('.jpg', frame)
#     data = pickle.dumps(buffer)
#     connection.sendall(data)


def msg_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        msg_length = client_socket.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = client_socket.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{addr}] {msg}")
            client_socket.send("Msg received".encode(FORMAT))
    client_socket.close()


def stream_client(client_socket, addr):
    while cap.isOpened():
        ret, frame = cap.read()
        data = pickle.dumps(frame)
        message_size = struct.pack("L", len(data))  # Pack a long
        client_socket.sendall(message_size + data)

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}")
    while True:
        conn, addr = server.accept()
        thread1 = threading.Thread(target=msg_client, args=(conn, addr))
        thread1.start()

        thread2 = threading.Thread(target=stream_client, args=(conn, addr))
        thread2.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting...")
start()
