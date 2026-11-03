
# Data Mapping - Convenience Retail Big Data

## 1. Dataset nguon

Nguon: https://www.kaggle.com/datasets/jessekeats/convenience-store

File: convenience_store.csv

- 18.531 giao dich
- 311 san pham
- Thoi gian: 2020-01-01 den 2023-12-30
- Tong gia tri giao dich: 936803.43
- Don vi tien te: chua xac minh

## 2. Anh xa CSV sang MySQL

### transactions

- Transaction_ID -> transaction_id
- Date -> transaction_date
- time_of_day -> transaction_time
- Customer_Name -> customer_name
- Customer_Category -> customer_category
- City -> city
- Payment_Method -> payment_method
- Season -> season
- Promotion -> promotion
- Member -> member
- Total_Items -> total_items
- Total_Cost -> total_cost

### products

- Product -> product_name
- product_id: tao tu danh sach ten san pham duy nhat

### transaction_items

- Transaction_ID -> transaction_id
- Product -> tach danh sach thanh tung san pham
- item_position -> vi tri san pham trong gio
- product_id -> lien ket bang products

## 3. Anh xa MySQL sang Hive

- transactions -> staging -> sales_fact
- products -> staging -> dim_product
- transaction_items -> staging -> basket_items_fact

Cac dimension khac duoc tao tu truong
mo ta cua transactions va du lieu thoi gian.

## 4. Nguyen tac du lieu

- Moi giao dich chi duoc tinh doanh thu mot lan.
- Khong suy dien City thanh StoreID.
- Khong coi Customer_Name la ma khach hang duy nhat.
- Khong gan Total_Cost cho tung san pham.
- Khong tu tao don gia san pham roi coi la du lieu goc.
- Du lieu benchmark mo rong phai duoc danh dau la mo phong.
- Giu nguyen file CSV Kaggle ban dau.
