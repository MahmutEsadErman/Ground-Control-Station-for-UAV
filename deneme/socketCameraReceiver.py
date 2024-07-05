import struct
import cv2
import socket
import pickle
import time
import collections

HEADER = 64
PORT = 5050
IP = "192.168.11.50"  # "78.188.55.182" public ip
ADDR = (IP, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(ADDR)

data = b""
payload_size = struct.calcsize("L")

prev_frame_time = 0
font = cv2.FONT_HERSHEY_SIMPLEX

# Define the length of the moving average filter and initialize it
filter_length = 10
fps_filter = collections.deque(maxlen=filter_length)

while True:
    while len(data) < payload_size:
        data += client_socket.recv(4096)
    packed_message_size = data[:payload_size]
    data = data[payload_size:]
    message_size = struct.unpack("L", packed_message_size)[0]

    while len(data) < message_size:
        data += client_socket.recv(4096)
    frame_data = data[:message_size]
    data = data[message_size:]

    frame = pickle.loads(frame_data)

    # Calculate FPS
    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time

    # Add the FPS to the filter and calculate the average
    fps_filter.append(fps)
    avg_fps = sum(fps_filter) / len(fps_filter)
    avg_fps = int(avg_fps)
    avg_fps = str(avg_fps)

    # Put FPS on the frame
    cv2.putText(frame, avg_fps, (10, 40), font, 1.5, (100, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client_socket.send(send_length)
    client_socket.send(message)
    print(client_socket.recv(2048).decode(FORMAT))


send("Hello Server!")

connected = True
while connected:
    send(input("Enter a message: "))
    if send(input("Enter a message: \n"
                  "Do you want to disconnect? (y/n) ")) == "y":
        send(DISCONNECT_MESSAGE)
        connected = False
