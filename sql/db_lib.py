from os.path import join
import sqlite3

def connect(): # apre la connessione al database, se non esiste lo crea
    filename_db = join("sql", "market.db")
    conn = sqlite3.connect(filename_db)
    conn.row_factory = sqlite3.Row
    return conn

def list_products(product): # ritorna tutti i prodotti nel database
    conn = connect()
    cur = conn.cursor()
    products = []
    if product == "la":
        cur.execute("SELECT seller_id, product_name FROM product")
        column_names = [description[0] for description in cur.description]
        for row in cur.fetchall():
            row_dict = {}
            for i, value in enumerate(row):
                row_dict[column_names[i]] = value
            products.append(row_dict)
    else:
        fetch_name = cur.execute("SELECT seller_id FROM product WHERE product_name = ?", (product,)).fetchall()
        try:
            products.append({'seller_id' : fetch_name[0], 'product_name' : product})
        except:
            print("diocane")
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
    if check_product(product, seller):
        cur.execute("DELETE FROM product WHERE product_name = ? AND seller_id = ?", (product, seller))
        conn.commit()
    conn.close()

def check_product(product, seller): # controlla se il prodotto selezionato esiste
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM product WHERE product_name = ? AND seller_id = ?", (product, seller))
    result = cur.fetchone()
    conn.close()
    return result[0] > 0

def init_db(): #Crea il database
    conn = connect()
    with open(join("sql", "market.sql"), encoding="utf-8") as f:
        conn.executescript(f.read())
    print("Database successfully created")
    conn.commit()
    conn.close()