
-- Database cho du an Convenience Retail
-- Tham khao Create_Tables.sql tu GitHub goc (commit 2c479a7)

CREATE DATABASE IF NOT EXISTS convenience_retail
CHARACTER SET utf8mb4;

USE convenience_retail;

-- 1. Bang luu thong tin giao dich
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id BIGINT PRIMARY KEY,
    transaction_date DATE NOT NULL,
    transaction_time TIME,
    customer_name VARCHAR(255),
    customer_category VARCHAR(80),
    city VARCHAR(255),
    payment_method VARCHAR(50),
    season VARCHAR(30),
    promotion VARCHAR(100),
    member VARCHAR(10),
    total_items INT NOT NULL,
    total_cost DECIMAL(12,2) NOT NULL
);

-- 2. Bang danh muc san pham
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL UNIQUE
);

-- 3. Bang chi tiet cac san pham trong moi giao dich
CREATE TABLE IF NOT EXISTS transaction_items (
    transaction_id BIGINT NOT NULL,
    item_position INT NOT NULL,
    product_id INT NOT NULL,

    PRIMARY KEY (transaction_id, item_position),

    FOREIGN KEY (transaction_id)
        REFERENCES transactions(transaction_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);
