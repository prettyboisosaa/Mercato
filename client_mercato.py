import socket
from threading import Thread
HOST = "127.0.0.1"
PORT = 8080

def sender():
    while True:
        msg = input()
        try:
            s.send(msg.encode())
        except:
            break

with socket.socket() as s:
    s.connect((HOST, PORT))
    Thread(target=sender).start()
    while True:
        try:
            print(s.recv(1024).decode(), end='')
        except:
            print("Server closed.")
            break