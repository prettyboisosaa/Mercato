PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS product (
    product_name TEXT,
    seller_id INTEGER,
    price NUMERIC(10, 2),
    quantity INTEGER,
    PRIMARY KEY (product_name, seller_id)
);
