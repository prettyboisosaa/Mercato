PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS product (
    product_name TEXT,
    seller_id INTEGER,
    price INTEGER,
    quantity INTEGER,
    PRIMARY KEY (product_name, seller_id)
);
