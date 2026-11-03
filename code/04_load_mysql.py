
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed"

# 1. Danh sach bang va cot can nap
TABLES = {
    "transactions": (
        "transaction_id transaction_date transaction_time customer_name "
        "customer_category city payment_method season promotion member "
        "total_items total_cost"
    ).split(),
    "products": "product_id product_name".split(),
    "transaction_items": "transaction_id item_position product_id".split(),
}

INTEGER = {"transaction_id", "product_id", "item_position", "total_items"}
NUMBER = INTEGER | {"total_cost"}


# 2. Chuyen gia tri CSV thanh gia tri SQL an toan
def sql_value(value, column):
    if value == "":
        return "NULL"
    if column in NUMBER:
        return str(int(value)) if column in INTEGER else str(value)
    return f"CONVERT(0x{value.encode('utf-8').hex()} USING utf8mb4)"


# 3. Tao lenh INSERT, moi lan 500 dong
def write_inserts(f, table, columns):
    with (DATA / f"{table}.csv").open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != columns:
            raise ValueError(f"Sai ten/thu tu cot trong {table}.csv")

        batch = []
        column_sql = ", ".join(f"`{c}`" for c in columns)
        count = 0

        for row in reader:
            values = ", ".join(sql_value(row[c], c) for c in columns)
            batch.append(f"({values})")
            count += 1

            if len(batch) == 500:
                f.write(f"INSERT INTO `{table}` ({column_sql}) VALUES "
                        + ",\n".join(batch) + ";\n")
                batch.clear()

        if batch:
            f.write(f"INSERT INTO `{table}` ({column_sql}) VALUES "
                    + ",\n".join(batch) + ";\n")

        return count


# 4. Kiem tra du lieu truoc khi nap
subprocess.run(
    [sys.executable, str(ROOT / "code/03_validate_data.py")],
    check=True
)

# 5. Nap MySQL theo thu tu khoa ngoai
with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as f:
    f.write("START TRANSACTION;\n")

    for table in ("transaction_items", "products", "transactions"):
        f.write(f"DELETE FROM `{table}`;\n")

    for table, columns in TABLES.items():
        print(f"Chuan bi {table}: {write_inserts(f, table, columns)} dong",
              flush=True)

    f.write("COMMIT;\n")
    f.write(
        "SELECT 'transactions' AS bang, COUNT(*) AS so_dong FROM transactions "
        "UNION ALL SELECT 'products', COUNT(*) FROM products "
        "UNION ALL SELECT 'transaction_items', COUNT(*) FROM transaction_items;\n"
    )

    f.seek(0)
    subprocess.run(
        ["sudo", "mysql", "--default-character-set=utf8mb4",
         "-D", "convenience_retail"],
        stdin=f,
        check=True
    )

print("NAP MYSQL THANH CONG")
