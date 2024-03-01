from os.path import join
import sqlite3

def connect(): # apre la connessione al database, se non esiste lo crea
    try:
        filename_db = join("sql", "market.db")
        conn = sqlite3.connect(filename_db)
        conn.row_factory = sqlite3.Row
        return conn
    except:
        return "Cannot connect to database."

def list_products(product):
    conn = connect()  # Make sure connect() function is defined elsewhere
    cur = conn.cursor()
    products = []
    if product == "la":
        cur.execute("SELECT seller_id, product_name, price, quantity FROM product")
        rows = cur.fetchall()
        for row in rows:
            seller_id, product_name, price, quantity = row
            products.append({'seller_id': seller_id, 'product_name': product_name, 'price': price, 'quantity': quantity})
    else:
        fetch_data = cur.execute("SELECT seller_id, price, quantity FROM product WHERE product_name = ?", (product,)).fetchall()
        try:
            for row in fetch_data:
                seller_id = row[0]
                price = row[1]
                quantity = row[2]
                products.append({'seller_id': seller_id, 'product_name': product, 'price': price, 'quantity': quantity})
        except IndexError:
            pass  
    conn.close()
    return products

def insert_product(product, seller, price, quantity): # inserisce i prodotti nel databse
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO product (product_name, seller_id, price, quantity) VALUES (?, ?, ?, ?)",(product, seller, price, quantity))
    conn.commit()
    conn.close()

def delete_product(product, seller): # elimina i prodotti dal databse
    conn = connect()
    cur = conn.cursor()
    if check_seller(product, seller):
        cur.execute("DELETE FROM product WHERE product_name = ? AND seller_id = ?", (product, seller))
        conn.commit()
        message = "product deleted."
    else:
        message = "the product doesnt exist: you cant delete."
    conn.close()
    return message

def delete_seller(seller):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM product WHERE seller_id = ?", (seller,))
    conn.commit()
    conn.close()

def check_product(product): # controlla se il prodotto selezionato esiste
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM product WHERE product_name = ?", (product,))
    result = cur.fetchone()
    conn.close()
    return result[0] > 0

def check_seller(product, seller): # controlla se il venditore ha un determinato prodotto
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM product WHERE product_name = ? AND seller_id = ?", (product, seller))
    result = cur.fetchone()
    conn.close()
    return result[0] > 0

def update_product(product, seller, quantity): # aggirona i prodotti sul database
    conn = connect()
    cur = conn.cursor()
    num_products = cur.execute('SELECT quantity FROM product WHERE seller_id = ? AND product_name = ?', (seller, product))
    if num_products == quantity:
        delete_product(product)
    else:
        new_quantity = int(num_products) - quantity
        cur.execute('UPDATE product SET quantity = ? WHERE seller_id = ? AND product_name = ?', (new_quantity, seller, product))
    conn.close()

def init_db(): # crea il database
    conn = connect()
    with open(join("sql", "market.sql"), encoding="utf-8") as f:
        conn.executescript(f.read())
    print("Database successfully created")
    conn.commit()
    conn.close()