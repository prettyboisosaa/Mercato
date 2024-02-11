import socket
from threading import Thread
HOST = "127.0.0.1"
PORT = 8080
index = 0
users = {}  # TODO: da fare con il DB
prices = {}

def listen_to_client(sock):            # function to select the type of client
    sock.send("Do you want to buy or to sell?".encode())
    global index
    while True:
        msg = sock.recv(8).decode()
        if msg in ["buy", "sell"]:
            if msg == "buy":
                users[str(index)] = {"conn" : sock, "mode" : "buy"}  # TODO: da fare con il DB
                Thread(target=listen_to_buyer, args=(sock,)).start()
            else:
                users[str(index)] = {"conn" : sock, "mode" : "sell", "products" : {}, "negotiating" : False, "turn" : False}  # TODO: da fare con il DB
                Thread(target=listen_to_seller, args=(sock, str(index))).start()
            index += 1
            return
        sock.send("You can only buy or sell.".encode())

def listen_to_buyer(sock):        # function to serve buyer clients
    while True:
        la = False
        sock.send("Write what you want to buy or 'la' to list all the aviable products.".encode())
        msg = sock.recv(1024).decode()
        if msg == "la":
            la = True
        flag_product = False
        product_list = ""
        #--------------TODO: da fare con il DB---------------
        for user, user_info in users.items():
            if user_info["mode"] == "sell":
                for info, value in user_info["products"].items():
                    if info == msg or la:
                        flag_product = True
                        product_list += f"seller: {user}, product: {info}, remaining: {value["quantity"]}, price each: {value["price"]}\n"
        #---------------------fine DB------------------------
        if flag_product:
            sock.send(product_list.encode())
            sock.send("Who do you want to buy from?".encode())
            seller_id = check_seller(sock, msg, la)
            negotiation(sock, seller_id)
        elif not la:
            sock.send(f"There's no one that sells {msg}".encode())
        else:
            sock.send("There are no items in the market at this moment.".encode())

def listen_to_seller(sock, id):     # function to serve seller clients
    sock.send("Press c to add/change you products or wait for somebody to buy them.".encode())
    while True:
        msg = sock.recv(256).decode()
        if msg == 'c':              # logic to add or change products
            sock.send("What do you want to add/change?".encode())
            msg = sock.recv(256).decode()
            sock.send(f"How many {msg} do you want to sell?".encode())
            msg2 = int_message(sock, "Only integers accepted.\nHow many of it do you want to sell?")
            sock.send("What is the price each?".encode())
            msg3 = int_message(sock, "Only integers accepted.\nWhat is its price?")
            try:
                users[id]["products"][msg] = {"product" : msg, "quantity" : msg2, "price" : msg3}   # TODO: da fare con il DB
                sock.send(f"Added/Changed: {msg}\nQuantity: {msg2}\nPrice each: {msg3}".encode())
            except:
                sock.send("Something went wrong, please try again.".encode())
            sock.send("Press c to add/change you products or wait for somebody to buy them.".encode())
        else:
            sock.send("Not implemented yet.".encode())  #TODO

def check_seller(sock, product, flag):    # checks if the seller chosen is aviable and has the right product
    valid_seller = False
    nvs_msg = "Seller not valid. Who do you want to buy from?".encode()
    while not valid_seller:
        seller = sock.recv(32).decode()
        try:
            if users[seller]["products"] and flag: # TODO: da fare con il DB
                return seller
            users[seller]["products"][product]["product"] == product # TODO: da fare con il DB
            valid_seller = True
        except:
            sock.send(nvs_msg)
    return seller

def int_message(sock, error_message):     # always returns an integer given by the client
    error_message = error_message.encode()
    int_msg = sock.recv(256).decode()
    while not isinstance(int_msg, int):
        try:
            int_msg = int(int_msg)
        except:
            sock.send(error_message)
            int_msg = sock.recv(256).decode()
    return int_msg

def negotiation(buyer_sock, seller_id):
    if users[seller_id]["negotiating"]:
        buyer_sock.send("Seller is already negotiating. Wait until he finishes...".encode())
    while users[seller_id]["negotiating"]:
        pass
    users[seller_id]["negotiating"] = True
    seller_sock = users[seller_id]["conn"]
    flush(buyer_sock)
    buyer_sock.send("Negotiation with seller started.\nOnly integers will be sent to the seller to negotiate.".encode())
    seller_sock.send("Negotiation with buyer started.\nOnly integers will be sent to the buyer to negotiate.".encode())
    prices[seller_id] = [0, 1]
    users[seller_id]["negotiating"] = False

def chatting(seller_id, buyer_sock):
    sock1 = users[seller_id]["conn"]
    nyt = "Not your turn".encode()
    while prices[seller_id][0] != prices[seller_id][1]:
        if users[seller_id]["turn"]:         # TODO: da fare con il DB
            users[seller_id]["turn"] = False
            value = int_message(sock1, "Only integers accepted.")
            buyer_sock.send(seller_msg.encode())
            seller_msg = sock1.recv(1024).decode()
        else:
            sock1.setblocking(0)
            if sock1.recv(1024):
                sock1.send(nyt)
            sock1.setblocking(1)

def flush(sock):
    try:
        sock.setblocking(0)
        while True:
            if not sock.recv(1024):
                break
    except:
        pass
    finally:
        sock.setblocking(1)

with socket.socket() as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Listening on port {PORT}...")
    while True:
        c, addr = s.accept()
        print('new connecton with adress: ', addr)
        Thread(target=listen_to_client, args=(c,)).start()