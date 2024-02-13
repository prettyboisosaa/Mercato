import socket
from threading import Thread
import sql.db_lib

HOST = "127.0.0.1"
PORT = 8080
index = 0
users = {}  # TODO: da fare con il DB
prices = {}

def listen_to_client(sock): # function to select the type of client
    sock.send("Do you want to buy or to sell?".encode())
    global index
    while True:
        msg = sock.recv(8).decode()
        if msg in ["buy", "sell"]:
            if msg == "buy":
                users[str(index)] = {"conn" : sock, "mode" : "buy"}  # TODO: da fare con il DB
                listen_to_buyer(sock)
            else:
                users[str(index)] = {"conn" : sock, "mode" : "sell", "negotiating" : False, "turn" : False}  # TODO: da fare con il DB
                listen_to_seller(sock, str(index))
            index += 1
            return
        sock.send("You can only buy or sell.".encode())

def listen_to_buyer(sock): # function to serve buyer clients
    while True:
        sock.send("Write what you want to buy or 'la' to list all the aviable products.".encode())
        product = sock.recv(1024).decode()
        sock.send(f"These are the available products:\n{db_lib.list_products(product)}".encode())
        if product == 'la':
            sock.send("Choose the product you want to buy".encode())
            while product := sock.recv(1024).decode() == 'la':
                sock.send("'la' is not an available product".encode())
        elif not product:
            sock.send("There are no items in the market at this moment.".encode())
        
        sock.send(f"These are the sellers who have {product}:\n{db_lib.list_products(product)}\nWho do you want to buy from?".encode())
        seller_id = sock.recv(1024).decode()
        while not db_lib.check_product(product, seller_id) and users[str(seller_id)]["negotiation"]:
            sock.send("The seller you have chosen is not available".encode())
            seller_id = sock.recv(1024).decode()
        negotiation(sock, seller_id)

# TODO: rivedere seller handling e implementarlo con il db
def listen_to_seller(sock, id): # function to serve seller clients
    sock.send("Press c to add/change you products or wait for somebody to buy them.".encode())
    while True:
        msg = sock.recv(256).decode()
        if msg == 'c': # logic to add or change products
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