PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS product;
CREATE TABLE product
(
    product_name VARCHAR,
    seller_id INTEGER,
    price INTEGER,
    quantity INTEGER,
    PRIMARY KEY (product_name, seller_id)
);