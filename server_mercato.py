import socket
from threading import Thread
from sql import db_lib

HOST = "0.0.0.0"
PORT = 8080
index = 0
users = {}
prices = {}

def listen_to_client(sock): # function to select the type of client
    try:
        sock.send("Do you want to buy or to sell?\n".encode())
        global index
        while True:
            flush(sock)
            msg = sock.recv(8).decode()
            if msg in ["buy", "sell"]:
                if msg == "buy":
                    users[str(index)] = {"conn" : sock, "mode" : "buy"}
                    Thread(target=listen_to_buyer, args=(sock, str(index))).start()
                else:
                    users[str(index)] = {"conn" : sock, "mode" : "sell", "negotiating" : False, "turn" : True}
                    Thread(target=listen_to_seller, args=(sock, str(index))).start()
                index += 1
                break
            else:
                sock.send("You can only buy or sell.\n".encode())
    except:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

def listen_to_buyer(sock, buyer_id): # function to serve buyer clients
    try:
        while True:
            sock.send("Write what you want to buy or 'la' to list all the available products.\nexit to close.\n".encode())
            product = sock.recv(1024).decode()
            product_list = db_lib.list_products(product)
            if product_list != []:
                sock.send(f"These are the available products:\n{product_list}\n".encode())
                if product == "la":
                    sock.send("Choose the product you want to buy.\n".encode())
                    while True:
                        product = sock.recv(1024).decode()
                        if db_lib.check_product(product):
                            break
                        else:
                            sock.send(f"{product} is not an available product.\nChoose a valid product.\n".encode())
                sock.send("Who do you want to buy from?\n".encode())
                while True:
                    seller_id = sock.recv(1024).decode()
                    if db_lib.check_seller(product, seller_id):
                        break
                    else:
                        sock.send("The seller you have chosen is not valid.\n".encode())
                negotiation(sock, seller_id)
                sock.send(f"What amount of {product} do you want to take?\n".encode())
                quantity = int_message(sock, "Quantity not valid.\n")
                db_lib.update_product(product, seller_id, quantity)
            else:
                if product == "la":
                    sock.send("There are no items in the market at this moment.\n".encode())
                else:
                    sock.send("What you searched is not available right now.\n".encode())
    except:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

def listen_to_seller(sock, seller_id): # function to serve seller clients
    try:
        while True:
            if not users[seller_id]["negotiating"]:
                sock.send("Press:\n c to add/change you products.\n d to delete a product.\nOr just wait for somebody to buy.\nexit to close.\n".encode())
                try:
                    sock.setblocking(0)
                    while True:
                        try:
                            msg = sock.recv(256).decode()
                            if msg or users[seller_id]["negotiating"]:
                                break
                        except:
                            continue
                except:
                    pass
                finally:
                    sock.setblocking(1)
                if users[seller_id]["negotiating"]:
                    msg = "skip"
                match msg:
                    case 'c': # logic to add or change products
                        sock.send("Which product do you want to add/change?\n".encode())
                        product = sock.recv(256).decode()
                        sock.send("What is the price each?\n".encode())
                        price = int_message(sock, "Only positive integers accepted.\nWhat is its price?\n")
                        sock.send(f"How many {product} do you want to sell?\n".encode())
                        quantity = int_message(sock, "Only positive integers accepted.\nHow many of it do you want to sell?\n")
                        try:
                            db_lib.insert_product(product, seller_id, price, quantity)
                            sock.send(f"Added/Changed: {product}\nQuantity: {quantity}\nPrice each: {price}\n".encode())
                        except:
                            sock.send("Something went wrong, please try again.\n".encode())
                    case 'd':
                        sock.send("Which product do you want to delete?\n".encode())
                        product = sock.recv(256).decode()
                        sock.send((db_lib.delete_product(product, seller_id) + '\n').encode())
                    case 'exit':
                        sock.shutdown(socket.SHUT_RDWR)
                        sock.close()
                        db_lib.delete_seller(seller_id)
                        break
                    case _:
                        if not users[seller_id]["negotiating"]:
                            sock.send("Command not valid\n".encode())
    except:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        
def negotiation(buyer_sock, seller_id): # controls that both the seller and the buyer are ready to chat
    try:
        if users[seller_id]["negotiating"]:
            buyer_sock.send("Seller is already negotiating. Wait until he finishes...\n".encode())
        while users[seller_id]["negotiating"]:
            pass
        users[seller_id]["negotiating"] = True
        seller_sock = users[seller_id]["conn"]
        flush(buyer_sock)
        buyer_sock.send("Negotiation with seller started.\nOnly integers will be sent to the seller to negotiate.\n".encode())
        seller_sock.send("Negotiation with buyer started.\nOnly integers will be sent to the buyer to negotiate.\n".encode())
        prices[seller_id] = [-1, -2]
        chatting(buyer_sock, seller_id)
        buyer_sock.send(f"Negotiation ended.\nFinal price: {prices[seller_id][0]}.\n".encode())
        seller_sock.send(f"Negotiation ended.\nFinal price: {prices[seller_id][0]}.\n".encode())
        users[seller_id]["negotiating"] = False
        del prices[seller_id]
    except:
        buyer_sock.shutdown(socket.SHUT_RDWR)
        buyer_sock.close()
        seller_sock.shutdown(socket.SHUT_RDWR)
        seller_sock.close()

def chatting(buyer_sock, seller_id): # function to make the seller and the buyer chat to agree on the price
    wait_turn = "Wait for your turn.\n".encode()
    your_turn = "It's your turn, write the price.\n".encode()
    seller_sock = users[seller_id]["conn"]
    while prices[seller_id][0] != prices[seller_id][1]:
        if users[seller_id]["turn"]:
            buyer_sock.send(wait_turn)
            seller_sock.send(your_turn)
            flush(seller_sock)
            price = int_message(seller_sock, "Only positive integer prices accepted.\n")
            prices[seller_id][0] = price
            buyer_sock.send((str(price)+'\n').encode())
            users[seller_id]["turn"] = False
        else:
            seller_sock.send(wait_turn)
            buyer_sock.send(your_turn)
            flush(buyer_sock)
            price = int_message(buyer_sock, "Only positive integer prices accepted.\n")
            prices[seller_id][1] = price
            seller_sock.send((str(price)+'\n').encode())
            users[seller_id]["turn"] = True
    users[seller_id]["turn"] = True

def int_message(sock, error_message): # always returns a positive integer given by the client
    try:
        error_message = error_message.encode()
        int_msg = sock.recv(256).decode()
        while not isinstance(int_msg, int):
            try:
                int_msg = int(int_msg)
                if int(int_msg) >= 0:
                    break
                else:
                    sock.send(error_message)
                    int_msg = sock.recv(256).decode()
            except:
                sock.send(error_message)
                int_msg = sock.recv(256).decode()     
    except:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        int_msg = -1
    return int_msg

def closeUsers(users):
    for index, user in users.items():
        user["conn"].shutdown(socket.SHUT_RDWR)
        user["conn"].close()

def flush(sock): # clears the read buffer
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
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Listening on port {PORT}...")
    while True:
        c, addr = s.accept()
        print('new connection with adress: ', addr)
        Thread(target=listen_to_client, args=(c,)).start()