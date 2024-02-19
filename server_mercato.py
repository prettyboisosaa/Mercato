import socket
from threading import Thread
from sql import db_lib

HOST = "127.0.0.1"
PORT = 8080
index = 0
users = {}
prices = {}

def listen_to_client(sock): # function to select the type of client
    sock.send("Do you want to buy or to sell?\n".encode())
    global index
    while True:
        msg = sock.recv(8).decode()
        if msg in ["buy", "sell"]:
            if msg == "buy":
                users[str(index)] = {"conn" : sock, "mode" : "buy"}
                listen_to_buyer(sock)
            else:
                users[str(index)] = {"conn" : sock, "mode" : "sell", "negotiating" : False, "turn" : False}
                listen_to_seller(sock, str(index))
            index += 1
            break
        else:
            sock.send("You can only buy or sell.\n".encode())

def listen_to_buyer(sock): # function to serve buyer clients
    while True:
        sock.send("Write what you want to buy or 'la' to list all the available products.\n".encode())
        product = sock.recv(1024).decode()
        product_list = db_lib.list_products(product)
        if product_list != []:
            sock.send(f"These are the available products:\n{product_list}\n".encode())
            if product == "la":
                sock.send("Choose the product you want to buy.\n".encode())
                while True:
                    product = sock.recv(1024).decode()
                    for prod in product_list:
                        if prod["product_name"] == product:
                            break
                    if prod["product_name"] == product:
                        break
                    sock.send(f"{product} is not an available product\nChoose a valid product.\n".encode())
            sock.send("Who do you want to buy from?\n".encode())
            seller_id = sock.recv(1024).decode()
            while True:
                if not db_lib.check_product(product, seller_id):
                    sock.send("The seller you have chosen is not valid.\n".encode())
                elif users[seller_id]["negotiating"]:
                    sock.send("The seller you have chosen is not available right now.\nTry again later or choose another seller.\n".encode())
                else:
                    break
                seller_id = sock.recv(1024).decode()
            negotiation(sock, seller_id)
        else:
            if product == "la":
                sock.send("There are no items in the market at this moment.\n".encode())
            else:
                sock.send("What you searched is not available right now.\n".encode())

def listen_to_seller(sock, seller_id): # function to serve seller clients
    while True:
        sock.send("Press:\n c to add/change you products.\n d to delete a product.\nOr just wait for somebody to buy.\n".encode())
        msg = sock.recv(256).decode()
        if msg == 'c': # logic to add or change products
            sock.send("Which product do you want to add/change?\n".encode())
            product = sock.recv(256).decode()
            sock.send("What is the price each?\n".encode())
            price = int_message(sock, "Only integers accepted.\nWhat is its price?\n")
            sock.send(f"How many {product} do you want to sell?\n".encode())
            quantity = int_message(sock, "Only integers accepted.\nHow many of it do you want to sell?\n")
            try:
                db_lib.insert_product(product, seller_id, price, quantity)
                sock.send(f"Added/Changed: {product}\nQuantity: {quantity}\nPrice each: {price}\n".encode())
            except:
                sock.send("Something went wrong, please try again.\n".encode())
        elif msg == 'd':
            sock.send("Which product do you want to delete?\n".encode())
            product = sock.recv(256).decode()
            db_lib.delete_product(product, seller_id)
        else:
            sock.send("Not implemented yet.\n".encode())  #TODO

def int_message(sock, error_message): # always returns an integer given by the client
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
        buyer_sock.send("Seller is already negotiating. Wait until he finishes...\n".encode())
    while users[seller_id]["negotiating"]:
        pass
    users[seller_id]["negotiating"] = True
    seller_sock = users[seller_id]["conn"]
    flush(buyer_sock)
    buyer_sock.send("Negotiation with seller started.\nOnly integers will be sent to the seller to negotiate.\n".encode())
    seller_sock.send("Negotiation with buyer started.\nOnly integers will be sent to the buyer to negotiate.\n".encode())
    prices[seller_id] = [0, 1]
    users[seller_id]["negotiating"] = False

def chatting(seller_id, buyer_sock):
    sock1 = users[seller_id]["conn"]
    nyt = "Not your turn\n".encode()
    while prices[seller_id][0] != prices[seller_id][1]:
        if users[seller_id]["turn"]:         # TODO: da fare con il DB
            users[seller_id]["turn"] = False
            value = int_message(sock1, "Only integers accepted.\n")
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

db_lib.init_db()
with socket.socket() as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Listening on port {PORT}...")
    while True:
        c, addr = s.accept()
        print('new connecton with adress: ', addr)
        Thread(target=listen_to_client, args=(c,)).start()