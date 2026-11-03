# Kiểm tra bộ dữ liệu Kaggle: Convenience Store

- Nguồn: https://www.kaggle.com/datasets/jessekeats/convenience-store
- Dữ liệu gốc: giữ nguyên trong `data/raw/kaggle_convenience_store/`
- Giới hạn đọc mỗi file dữ liệu: 50,000 dòng (nếu đạt giới hạn thì không phải tổng số dòng).

## Danh sách file

- `data/raw/kaggle_convenience_store/.complete/datasets/jessekeats/convenience-store/1/bundle.complete` — 0.00 MiB
- `data/raw/kaggle_convenience_store/convenience_store.csv` — 3.44 MiB

## Cấu trúc dữ liệu

### bundle.complete
Chưa tự động đọc định dạng này.

### convenience_store.csv
- Số dòng: **18,531** (đầy đủ).
- Số cột: **13**.
- Các cột: `Transaction_ID`, `Date`, `Customer_Name`, `Product`, `Total_Items`, `Total_Cost`, `Payment_Method`, `City`, `time_of_day`, `Customer_Category`, `Season`, `Promotion`, `Member`
- Mã giao dịch: `Transaction_ID`
- Sản phẩm: `Product`, `Total_Items`
- Đơn giá / doanh thu: `Total_Items`, `Total_Cost`
- Ngày giờ: `Date`, `time_of_day`
- Khách hàng: `Customer_Name`, `Customer_Category`, `Member`
- Kiểm tra giỏ hàng trong mẫu: 0 mã giao dịch chứa ít nhất 2 giá trị sản phẩm khác nhau, trên 18,531 mã giao dịch.
- Một số bản ghi đầu:
```json
{"Transaction_ID": "1000000000", "Date": "2022-06-20", "Customer_Name": "Michael Young", "Product": "['Tea', 'Swim Cap', 'Sandals', 'Slippers']", "Total_Items": "4", "Total_Cost": "38.27", "Payment_Method": "Cash", "City": "Eduardoberg", "time_of_day": "13:24:15", "Customer_Category": "Adult (30-49)", "Season": "Winter", "Promotion": "Discount on Selected Items", "Member": "No"}
{"Transaction_ID": "1000000001", "Date": "2023-07-23", "Customer_Name": "Lindsay Simmons", "Product": "['Band-Aids', 'Lighter Fluid', 'Beef']", "Total_Items": "3", "Total_Cost": "21.630000000000003", "Payment_Method": "Cash", "City": "Mariaton", "time_of_day": "09:56:29", "Customer_Category": "Young Adult (20-29)", "Season": "Winter", "Promotion": "Discount on Selected Items", "Member": "No"}
{"Transaction_ID": "1000000002", "Date": "2021-10-28", "Customer_Name": "Mrs. Jessica Reed", "Product": "['Onion Powder', 'Dish Soap', 'Salt', 'Aluminum Foil', 'Charcoal']", "Total_Items": "5", "Total_Cost": "43.190000000000005", "Payment_Method": "Mobile Payment", "City": "Strongview", "time_of_day": "18:29:29", "Customer_Category": "Adult (30-49)", "Season": "Summer", "Promotion": "BOGO (Buy One Get One)", "Member": "No"}
```

## Đối chiếu sơ bộ đề cương

- **Mã giao dịch:** `Transaction_ID`
- **Sản phẩm:** `Product`, `Total_Items`
- **Số lượng:** Chưa phát hiện cột tương ứng
- **Đơn giá / doanh thu:** `Total_Cost`, `Total_Items`
- **Cửa hàng:** Chưa phát hiện cột tương ứng
- **Ngày giờ:** `Date`, `time_of_day`
- **Khách hàng:** `Customer_Category`, `Customer_Name`, `Member`

**Cảnh báo:** Tên cột chỉ giúp phát hiện sơ bộ. Cần kiểm tra khóa và quan hệ giữa các bảng, tính hợp lệ của số tiền, mã giao dịch, và chất lượng dữ liệu trước khi thiết kế Star Schema.
Sự tồn tại của mã giao dịch và mã sản phẩm không tự động chứng minh có giỏ hàng nhiều sản phẩm.
