import socket
from threading import Thread
HOST = "127.0.0.1"
PORT = 8080

def sender():
    while True:
        msg = input()
        s.send(msg.encode())


with socket.socket() as s:
    s.connect((HOST, PORT))
    t1 = Thread(target=sender).start()
    while True:
        print(s.recv(2048).decode())
