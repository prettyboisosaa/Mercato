import socket
from threading import Thread
HOST = "127.0.0.1"
PORT = 8080

def sender():
    try:
        while True:
            msg = input()
            try:
                s.send(msg.encode())
            except:
                break
    except:
        s.shutdown(socket.SHUT_RDWR)
        s.close()

with socket.socket() as s:
    try:
        s.connect((HOST, PORT))
        Thread(target=sender).start()
        while True:
            try:
                print(s.recv(1024).decode(), end='')
            except:
                print("Server closed.")
                break
    except:
        s.shutdown(socket.SHUT_RDWR)
        s.close()