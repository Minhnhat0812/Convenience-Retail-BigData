
# Star Schema - Convenience Retail Big Data

## 1. Nguồn dữ liệu

- Dataset: Convenience Store - Kaggle (jessekeats)
- Giao dịch: 18.531
- Sản phẩm khác nhau: 311
- Thời gian: 2020-01-01 đến 2023-12-30

## 2. Mô hình MySQL nguồn

- transactions
- products
- transaction_items

## 3. Mô hình Hive Star Schema

### Dimension

1. dim_date
   - date_key (PK)
   - full_date
   - day
   - month
   - quarter
   - year

2. dim_customer_segment
   - segment_key (PK)
   - customer_category
   - member

3. dim_location
   - location_key (PK)
   - city

4. dim_payment
   - payment_key (PK)
   - payment_method

5. dim_promotion
   - promotion_key (PK)
   - promotion

6. dim_product
   - product_key (PK)
   - product_name

### Fact

7. sales_fact
   - transaction_id (PK)
   - date_key (FK)
   - segment_key (FK)
   - location_key (FK)
   - payment_key (FK)
   - promotion_key (FK)
   - transaction_time
   - total_items
   - total_cost

   Grain: 1 dong = 1 giao dich.

8. basket_items_fact
   - transaction_id
   - item_position
   - product_key (FK)

   Grain: 1 dong = 1 vi tri san pham
   trong 1 giao dich.

   Khoa duy nhat:
   (transaction_id, item_position)

   transaction_id lien ket den sales_fact.

## 4. Cac chi so phan tich

- Total Revenue = SUM(total_cost) tu sales_fact
- Total Transactions = COUNT(*) tu sales_fact
- AOV = Total Revenue / Total Transactions
- Average Basket Size = AVG(total_items)
- Product Frequency = So gio hang chua san pham
- Support, Confidence, Lift cho cap san pham

## 5. Gioi han du lieu

- Chua co StoreID thuc te.
- Chua co ma khach hang on dinh.
- Chua co gia ban rieng tung san pham.
- Khong gan total_cost cho tung san pham.
- Khong tinh doanh thu theo san pham
  neu chua co du lieu bo sung.
- Khong suy luan City la cua hang.
- benchmark mo rong phai tach voi du lieu goc.

## 6. Ke hoach trien khai

Giai doan 4: Xu ly Kaggle, nap MySQL.
Giai doan 5: Sqoop -> HDFS.
Giai doan 6: Tao bang Hive staging.
Giai doan 7: Tao dimension va fact.
Giai doan 8: Phan tich doanh thu.
Giai doan 9: Market Basket Analysis.
Giai doan 10: Power BI.
Giai doan 11: Benchmark TextFile va ORC.
