import socket
from threading import Thread
HOST = "127.0.0.1"
PORT = 8080
index = 0
users = {}

def listen_to_client(sock):            # function to select the type of client
    sock.send("Do you want to buy or to sell?".encode())
    global index
    while True:
        msg = sock.recv(1024).decode()
        if msg in ["buy", "sell"]:
            if msg == "buy":
                users[index] = {"conn" : sock, "mode" : "buy"}
                t2 = Thread(target=listen_to_buyer, args=(sock, index)).start()
            else:
                users[index] = {"conn" : sock, "mode" : "sell", "products" : {}}
                t3 = Thread(target=listen_to_seller, args=(sock, index)).start()
            index = index + 1
            return
        sock.send("You can only buy or sell.".encode())

def listen_to_buyer(sock, id):        # function to serve buyer clients
    while True:
        la = False
        sock.send("Write what you want to buy or 'la' to list all the aviable products.".encode())
        msg = sock.recv(1024).decode()
        if msg == "la":
            la = True
        flag_product = False
        product_list = ""
        #--------------TODO: gestione database---------------
        for user, user_info in users.items():
            if user_info["mode"] == "sell":
                for info, value in user_info["products"].items():
                    if info == msg or la:
                        flag_product = True
                        product_list += f"seller: {user}, product: {info}, remaining: {value["quantity"]}, price each: {value["price"]}\n"
        #--------------fine gestione database------------
        if flag_product:
            sock.send(product_list.encode())
            sock.send("Who do you want to buy from?".encode())
            seller = sock.recv(1024).decode()
        elif not la:
            sock.send(f"There's no one that sells {msg}".encode())
        else:
            sock.send("There are no items in the market at this moment.".encode())

def listen_to_seller(sock, id):        # function to serve seller clients
    sock.send("Press c to add/change you products or wait for somebody to buy them.".encode())
    while True:
        msg = sock.recv(1024).decode()
        if msg == 'c':             # logic to add or change products
            sock.send("What do you want to add/change?".encode())
            msg = sock.recv(1024).decode()
            sock.send(f"How many {msg} do you want to sell?".encode())
            msg2 = sock.recv(1024).decode()
            while not isinstance(msg2, int):
                try:
                    msg2 = int(msg2)
                except:
                    sock.send("Only integers accepted.\nHow many of it do you want to sell?".encode())
                    msg2 = sock.recv(1024).decode()
            sock.send("What is the price each?".encode())
            msg3 = sock.recv(1024).decode()
            while not isinstance(msg3, int):
                try:
                    msg3 = int(msg3)
                except:
                    sock.send("Only integers accepted.\nWhat is its price?".encode())
                    msg3 = sock.recv(1024).decode()
            try:
                users[id]["products"][msg] = {"product" : msg, "quantity" : msg2, "price" : msg3}
                sock.send(f"Added/Changed: {msg}\nQuantity: {msg2}\nPrice each: {msg3}".encode())
            except:
                sock.send("Something went wrong, please try again.".encode())
            sock.send("Press c to add/change you products or wait for somebody to buy them.".encode())
        else:
            sock.send("Not implemented yet.".encode())  #TODO

with socket.socket() as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Listening on port {PORT}...")
    while True:
        c_c, addr = s.accept()
        print('new connecton with adress: ', addr)
        t1 = Thread(target=listen_to_client, args=(c_c,)).start()