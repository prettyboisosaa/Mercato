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
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            break
        if msg == "exit":
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            break

with socket.socket() as s:
    try:
        s.connect((HOST, PORT))
        t = Thread(target=sender)
        t.daemon = True
        t.start()
        while True:
            try:
                print(s.recv(1024).decode(), end='')
            except:
                print("Server closed.")
                exit()
    except:
        s.shutdown(socket.SHUT_RDWR)
        s.close()