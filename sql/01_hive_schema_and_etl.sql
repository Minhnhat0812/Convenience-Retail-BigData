-- Ép Hive chạy Local Mode để vượt qua lỗi tràn RAM/resource trên WSL2
set hive.exec.mode.local.auto=true;

CREATE DATABASE IF NOT EXISTS retail_dw;
USE retail_dw;

-- Dọn dẹp bảng cũ nếu có
DROP TABLE IF EXISTS staging_transactions;
DROP TABLE IF EXISTS dim_time;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_promotion;
DROP TABLE IF EXISTS dim_payment;
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS fact_transaction_items;

-- 1. Tạo bảng Staging trỏ đúng vào thư mục HDFS chứa dữ liệu
CREATE EXTERNAL TABLE staging_transactions (
    Transaction_ID BIGINT, Date_str STRING, Customer_Name STRING, 
    Product STRING, Total_Items INT, Total_Cost DOUBLE, 
    Payment_Method STRING, City STRING, time_of_day STRING, 
    Customer_Category STRING, Season STRING, Promotion STRING, Member STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    "separatorChar" = ",",
    "quoteChar"     = "\""
)
LOCATION '/retail_data'
TBLPROPERTIES ("skip.header.line.count"="1");

-- 2. Tạo các bảng Chiều (Dimension Tables)
CREATE TABLE dim_time AS
SELECT DISTINCT Date_str, year(Date_str) AS trans_year, month(Date_str) AS trans_month, quarter(Date_str) AS trans_quarter, Season
FROM staging_transactions;

CREATE TABLE dim_customer AS
SELECT DISTINCT Customer_Name, Customer_Category, Member
FROM staging_transactions;

CREATE TABLE dim_promotion AS SELECT DISTINCT Promotion FROM staging_transactions;
CREATE TABLE dim_payment AS SELECT DISTINCT Payment_Method FROM staging_transactions;

-- 3. Tạo các bảng Sự kiện (Fact Tables và ETL bóc tách mảng sản phẩm)
CREATE TABLE fact_sales AS
SELECT Transaction_ID, Date_str, Customer_Name, Payment_Method, Promotion, Total_Items, Total_Cost
FROM staging_transactions;

-- Bước 1: Xóa bảng tạm nếu đã tồn tại
DROP TABLE IF EXISTS tmp_fact_items;

CREATE TABLE IF NOT EXISTS fact_transaction_items (
    Transaction_ID BIGINT,
    product_name STRING
);
-- Bước 2: Tạo bảng tạm và bóc tách dữ liệu
CREATE TABLE tmp_fact_items AS
SELECT 
    Transaction_ID, 
    TRIM(pn) AS product_name
FROM staging_transactions
LATERAL VIEW explode(split(translate(Product, '[]\'', ''), ',')) t AS pn
WHERE TRIM(pn) != 'NULL' AND TRIM(pn) != '';

-- Bước 3: Chèn dữ liệu vào bảng chính
INSERT OVERWRITE TABLE fact_transaction_items
SELECT * FROM tmp_fact_items;