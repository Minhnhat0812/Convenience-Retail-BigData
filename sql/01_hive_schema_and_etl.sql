CREATE DATABASE IF NOT EXISTS retail_dw;
USE retail_dw;

-- 1. Tạo bảng Staging để hứng dữ liệu thô từ HDFS
CREATE EXTERNAL TABLE IF NOT EXISTS staging_transactions (
    Transaction_ID BIGINT, Date_str STRING, Customer_Name STRING, 
    Product STRING, Total_Items INT, Total_Cost DOUBLE, 
    Payment_Method STRING, City STRING, time_of_day STRING, 
    Customer_Category STRING, Season STRING, Promotion STRING, Member STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' 
TBLPROPERTIES ("skip.header.line.count"="1");

-- (Giả định dữ liệu đã được load từ HDFS vào bảng staging_transactions)

-- 2. Tạo Dimension Tables (Bảng Chiều)
CREATE TABLE dim_time AS
SELECT DISTINCT Date_str, year(Date_str) AS trans_year, month(Date_str) AS trans_month, quarter(Date_str) AS trans_quarter, Season
FROM staging_transactions;

CREATE TABLE dim_customer AS
SELECT DISTINCT Customer_Name, Customer_Category, Member
FROM staging_transactions;

CREATE TABLE dim_promotion AS SELECT DISTINCT Promotion FROM staging_transactions;
CREATE TABLE dim_payment AS SELECT DISTINCT Payment_Method FROM staging_transactions;

-- 3. Tạo Fact Tables (Bảng Sự Kiện)
-- Fact Doanh thu tổng hợp
CREATE TABLE fact_sales AS
SELECT Transaction_ID, Date_str, Customer_Name, Payment_Method, Promotion, Total_Items, Total_Cost
FROM staging_transactions;

-- Fact Chi tiết Giỏ hàng (ETL bóc tách mảng "['A', 'B']" thành các dòng riêng biệt)
CREATE TABLE fact_transaction_items AS
SELECT Transaction_ID, TRIM(product_name) AS product_name
FROM staging_transactions
LATERAL VIEW explode(split(regexp_replace(Product, '\\[|\\]|\\'', ''), ',')) exploded_table AS product_name;