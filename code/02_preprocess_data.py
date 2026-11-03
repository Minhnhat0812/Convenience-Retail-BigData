import ast
import csv
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/kaggle_convenience_store/convenience_store.csv"
OUTPUT = ROOT / "data/processed"
OUTPUT.mkdir(parents=True, exist_ok=True)

# 1. Doc va chuan hoa giao dich
columns = {
    "transaction_date": "Date",
    "transaction_time": "time_of_day",
    "customer_name": "Customer_Name",
    "customer_category": "Customer_Category",
    "city": "City",
    "payment_method": "Payment_Method",
    "season": "Season",
    "promotion": "Promotion",
    "member": "Member"
}

transactions, baskets, product_names = [], [], set()
seen_ids = set()

with SOURCE.open(encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f):
        tid = int(row["Transaction_ID"])
        basket = ast.literal_eval(row["Product"])
        amount = Decimal(row["Total_Cost"]).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        if tid in seen_ids:
            raise ValueError(f"Trung ma giao dich: {tid}")
        if not isinstance(basket, list) or not all(
            isinstance(p, str) and p.strip() for p in basket
        ):
            raise ValueError(f"Gio hang khong hop le: {tid}")
        if not basket or len(basket) != int(row["Total_Items"]):
            raise ValueError(f"Sai so luong san pham: {tid}")
        if amount <= 0:
            raise ValueError(f"Tong tien khong hop le: {tid}")

        seen_ids.add(tid)
        product_names.update(basket)
        baskets.append((tid, basket))

        transactions.append({
            "transaction_id": tid,
            **{new: row[old] for new, old in columns.items()},
            "total_items": len(basket),
            "total_cost": str(amount)
        })

# 2. Tao danh muc san pham
product_ids = {
    name: i for i, name in enumerate(sorted(product_names), 1)
}

products = [
    {"product_id": pid, "product_name": name}
    for name, pid in product_ids.items()
]

# 3. Tach chi tiet gio hang
transaction_items = [
    {"transaction_id": tid, "item_position": pos, "product_id": product_ids[name]}
    for tid, basket in baskets
    for pos, name in enumerate(basket, 1)
]

# 4. Xuat CSV
def save_csv(filename, data):
    with (OUTPUT / filename).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

save_csv("transactions.csv", transactions)
save_csv("products.csv", products)
save_csv("transaction_items.csv", transaction_items)

print("Giao dich:", len(transactions))
print("San pham:", len(products))
print("Chi tiet gio hang:", len(transaction_items))
print("Tong gia tri:", sum(Decimal(r["total_cost"]) for r in transactions))
