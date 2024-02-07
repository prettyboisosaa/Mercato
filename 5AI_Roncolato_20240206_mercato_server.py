import socket
from threading import Thread
HOST = "127.0.0.1"
PORT = 8080
users = {}

def listen_to_client(sock):
    sock.send("Do you want to buy or to sell?".encode())
    while True:
        msg = sock.recv(1024).decode()
        if msg in ["buy", "sell"]:
            if msg == "buy":
                users[sock] = {"conn" : sock, "mode" : "buy"}
                t2 = Thread(target=listen_to_buyer, args=(sock,)).start()
                return
            else:
                users[sock] = {"conn" : sock, "mode" : "sell", "products" : {}}
                t3 = Thread(target=listen_to_seller, args=(sock,)).start()
                return
        sock.send("You can only buy or sell.".encode())

def listen_to_buyer(sock):
    sock.send("What do you want to buy?".encode())

def listen_to_seller(sock):
    sock.send("Press c to add/change you products or wait for somebody to buy them.".encode())
    while True:
        msg = sock.recv(1024).decode()
        if msg == 'c':
            try:
                sock.send("What do you want to add/change?".encode())
                msg = sock.recv(1024).decode()
                sock.send(f"How many {msg} do you want to sell?".encode())
                msg2 = sock.recv(1024).decode()
                while not isinstance(msg2, int):
                    sock.send("Only integers accepted.\nHow many of it do you want to sell?".encode())
                    msg2 = sock.recv(1024).decode()
                sock.send("What is the price each?".encode())
                msg3 = sock.recv(1024).decode()
                while not isinstance(msg3, int):
                    sock.send("Only integers accepted.\nWhat is its price?".encode())
                    msg3 = sock.recv(1024).decode()
                users[sock]["products"][msg] = {"product" : msg, "quantity" : int(msg2), "price" : int(msg3)}
                sock.send(f"Added/Changed: {msg}\nQuantity: {msg2}\nPrice each: {msg3}")
            except:
                sock.send("Something went wrong, please try again.")
        else:
            sock.send("Not implemented yet.".encode())

with socket.socket as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Listening on port {PORT}...")
    while True:
        c_c, addr = s.accept()
        print('new connecton with adress: ', addr)
        t1 = Thread(target=listen_to_client, args=(c_c,)).start()