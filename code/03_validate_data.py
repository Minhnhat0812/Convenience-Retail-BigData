
import csv
from pathlib import Path
from collections import Counter
from datetime import date, time
from decimal import Decimal

DATA = Path(__file__).resolve().parents[1] / "data/processed"

# 1. Doc 3 file CSV
def read_csv(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

transactions = read_csv("transactions.csv")
products = read_csv("products.csv")
items = read_csv("transaction_items.csv")

# 2. Kiem tra khoa chinh va khoa ngoai
tids = [r["transaction_id"] for r in transactions]
pids = [r["product_id"] for r in products]
keys = [(r["transaction_id"], r["item_position"]) for r in items]

assert len(tids) == len(set(tids)), "Trung giao dich"
assert len(pids) == len(set(pids)), "Trung ma san pham"
assert len(keys) == len(set(keys)), "Trung chi tiet gio hang"
assert len({r["product_name"] for r in products}) == len(products)

tid_set = set(tids)
pid_set = set(pids)

assert all(
    r["transaction_id"] in tid_set and r["product_id"] in pid_set
    for r in items
), "Sai khoa ngoai"

# 3. Kiem tra du lieu phan tich
counts = Counter(r["transaction_id"] for r in items)
required = [
    "transaction_date", "payment_method", "promotion",
    "customer_category", "member", "season", "total_items"
]

for r in transactions:
    assert all(r[c].strip() for c in required), "Thieu du lieu phan tich"
    assert counts[r["transaction_id"]] == int(r["total_items"]), "Sai gio hang"
    date.fromisoformat(r["transaction_date"])
    time.fromisoformat(r["transaction_time"])
    assert Decimal(r["total_cost"]) > 0, "Tong tien khong hop le"

# 4. In ket qua
revenue = sum(Decimal(r["total_cost"]) for r in transactions)

print("Giao dich:", len(transactions))
print("San pham:", len(products))
print("Chi tiet gio hang:", len(items))
print("Tong gia tri:", revenue)
print("Khoa, gio hang va du lieu phan tich: HOP LE")
