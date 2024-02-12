from os.path import join
import sqlite3

def connect():
    filename_db = join("sql", "market.db")
    conn = sqlite3.connect(filename_db)
    conn.row_factory = sqlite3.Row
    return conn

def list_products(product):
    conn = connect()
    cur = conn.cursor()
    products = None
    
    if product == "la":
        products = cur.execute("SELECT seller_id, product_name FROM product")
    else:
        products = cur.execute("SELECT seller_id, product_name FROM product WHERE product = ?", (product))
    
    con.close()
    return products

def check_product(product, seller):
    conn = connect()
    cur = conn.cursor()

    if product != "la":
        cur.execute("SELECT COUNT(*) FROM product WHERE product_name = ? AND seller_id = ?", (product, seller))
        result = cur.fetchone()
        
        conn.close()
        return result[0] > 0
    return False # you cannot select 'la' as a product

def insert_product(product, seller, price, quantity):
    conn = connect()
    cur = conn.cursor()

    cur.execute("INSERT INTO product (product_name, seller_id, price, quantity) VALUES (?, ?, ?, ?)",
                (product, seller, price, quantity))
    conn.commit()
    conn.close()

def delete_product(product, seller):
    conn = connect()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM product WHERE product_name = ? AND seller_id = ?", (product, seller))
    
    conn.commit()
    conn.close()

def init_db():
    """Crea il database"""
    conn = connect()

    with open(join("sql", "market_db.sql"), encoding="utf-8") as f:
        conn.executescript(f.read())

    print("Database successfully created")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()