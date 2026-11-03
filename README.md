# Convenience Retail Big Data — Hadoop Pipeline

Dự án phân tích giao dịch bán lẻ chuỗi cửa hàng tiện lợi theo mô hình **batch**.

**Luồng dữ liệu:** Kaggle → Python (chuẩn hóa & kiểm tra) → MySQL (`convenience_retail`) → Sqoop → HDFS → Hive → Power BI.

**Tiến độ:** Hoàn thành giai đoạn 1–5 trên máy thành viên 1; Hive, phân tích, Power BI và benchmark sẽ được các thành viên tiếp tục phát triển. Repo không chứa phần mềm Hadoop, dịch vụ MySQL hay dữ liệu HDFS đã chạy.

## 1. Yêu cầu môi trường

Ưu tiên **Windows + WSL2 Ubuntu 22.04**, VS Code WSL. Máy đã cài và cấu hình được:

| Thành phần | Phiên bản tham chiếu của thành viên 1 |
|---|---|
| Python | 3.10.12 |
| Java | 8 |
| Hadoop | 3.2.1 |
| Hive | 3.1.2 |
| Sqoop | 1.4.7 |
| MySQL | 8.0.x |
| SSH | Phục vụ Hadoop pseudo-distributed |

Cần có `java`, `hdfs`, `start-dfs.sh`, `start-yarn.sh`, `sqoop`, `mysql`, `sudo mysql` hoạt động trong Terminal Ubuntu. Các thành viên phải cài các hệ thống này trên máy riêng trước khi chạy pipeline. Cấu hình môi trường không được tự động thiết lập bởi Git clone.

## 2. Clone và chuẩn bị Python

```bash
git clone https://github.com/Minhnhat0812/Convenience-Retail-BigData.git
cd Convenience-Retail-BigData
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. Lấy dữ liệu Kaggle và tiền xử lý

Nguồn: [Convenience Store — jessekeats (Kaggle)](https://www.kaggle.com/datasets/jessekeats/convenience-store).

```bash
python code/00_download_dataset.py
python code/02_preprocess_data.py
python code/03_validate_data.py
```

Nếu Kaggle yêu cầu đăng nhập hoặc chấp thuận điều khoản dataset, từng thành viên thực hiện với tài khoản riêng; không đưa token lên GitHub.

Script tải dữ liệu về `data/raw/kaggle_convenience_store/convenience_store.csv`. File `01_inspect_dataset.py` là bước khảo sát dữ liệu tùy chọn. Dữ liệu raw và processed được tạo lại trên từng máy, không commit lên GitHub (cần tuân thủ giấy phép nguồn Kaggle).

Kết quả kỳ vọng với phiên bản dữ liệu nhóm đã kiểm tra:

| CSV / bảng | Số dòng |
|---|---:|
| transactions | 18.531 |
| products | 311 |
| transaction_items | 89.564 |

Tổng `total_cost` giao dịch là **936803.43** (chưa xác minh đơn vị tiền tệ). Nếu số liệu từ Kaggle thay đổi do cập nhật dataset, cần kiểm tra phiên bản nguồn trước khi tiếp tục.

## 4. Tạo MySQL và nạp dữ liệu

```bash
sudo service mysql start
sudo mysql < sql/mysql/create_tables.sql
python code/04_load_mysql.py
```

`04_load_mysql.py` tự gọi bước kiểm tra dữ liệu và **xóa/nạp lại ba bảng** `transactions`, `products`, `transaction_items` trong database `convenience_retail`. Không chạy trên database có dữ liệu riêng cần giữ lại.

Kiểm tra:

```bash
sudo mysql -D convenience_retail -e "SELECT COUNT(*) FROM transactions; SELECT COUNT(*) FROM products; SELECT COUNT(*) FROM transaction_items;"
```

## 5. Cho phép Sqoop đọc MySQL

Tạo tài khoản SQL chỉ có quyền đọc trên máy mới bằng `sudo mysql` (trong MySQL shell, thay `MAT_KHAU_RIENG` bằng mật khẩu tự chọn, không commit hoặc gửi mật khẩu):

```sql
CREATE USER IF NOT EXISTS 'sqoopuser'@'127.0.0.1' IDENTIFIED BY 'MAT_KHAU_RIENG';
GRANT SELECT ON convenience_retail.* TO 'sqoopuser'@'127.0.0.1';
```

Nếu tài khoản đã tồn tại, xác định đúng mật khẩu và Host trước khi chạy. Có thể thử bằng:

```bash
sqoop list-tables --connect jdbc:mysql://127.0.0.1:3306/convenience_retail --username sqoopuser -P
```

Kết quả cần liệt kê `products`, `transactions`, `transaction_items`.

## 6. Khởi động Hadoop và import lên HDFS

```bash
sudo service ssh start
start-dfs.sh
start-yarn.sh
jps
bash scripts/01_import_sqoop.sh
```

`jps` cần thấy ít nhất NameNode, DataNode, SecondaryNameNode, ResourceManager, NodeManager. Bash import hỏi mật khẩu Sqoop ba lần; dữ liệu lưu vào `/user/<ten-user-Ubuntu>/convenience_retail/raw/`.

**Cảnh báo:** `scripts/01_import_sqoop.sh` dùng `--delete-target-dir` nên mỗi lần chạy sẽ xóa thư mục đích HDFS của ba bảng trước khi import lại. Không chạy đồng thời với tác vụ đang đọc các thư mục đó.

Kiểm tra HDFS:

```bash
for table in products transactions transaction_items; do
  echo "===== $table ====="
  hdfs dfs -test -e "/user/$(whoami)/convenience_retail/raw/$table/_SUCCESS" || exit 1
  hdfs dfs -cat "/user/$(whoami)/convenience_retail/raw/$table/part-m-*" | wc -l
done
```

Số dòng cần khớp lần lượt **311, 18531, 89564**. Các file HDFS được tạo ở định dạng text với ký tự phân tách trường `\001` (Ctrl-A). Khi tạo bảng Hive external cần khai báo đúng dấu phân tách này.

## 7. Phân công

- **Thành viên 1:** Kaggle, Python, MySQL, Sqoop, HDFS; mã nguồn `code/`, `sql/mysql/`, `scripts/`.
- **Thành viên 2:** Hive staging/cleaning, dimensional model & 9 câu hỏi phân tích; tạo script tại `sql/hive/`. Tài liệu tham khảo `docs/star_schema_design.md`.
- **Thành viên 3:** Dashboard Power BI, benchmark; dùng `powerbi/`, `benchmark/`.

Dùng nhánh Git riêng cho từng thành viên, tạo Pull Request để gộp vào `main`. Không commit `.env`, token, mật khẩu, dữ liệu MySQL/HDFS hay `.venv`.

## 8. Giới hạn dữ liệu

Dataset không cung cấp mã cửa hàng đáng tin cậy, ID khách hàng bền vững hoặc doanh thu riêng từng sản phẩm. `total_cost` là **tổng tiền giao dịch**, không phải doanh thu của mỗi dòng sản phẩm. Không được nhân tổng tiền cho từng dòng `transaction_items` khi phân tích. Cột `City` không phải mã cửa hàng.

## 9. Nguồn tham khảo

- [Kaggle convenience-store](https://www.kaggle.com/datasets/jessekeats/convenience-store)
- [GitHub reference: E-Commerce-data-analysis-using-Hadoop](https://github.com/abhinaba-fbr/E-Commerce-data-analysis-using-Hadoop) (khảo sát ý tưởng, không commit thư mục `original-project/` vào repo).
