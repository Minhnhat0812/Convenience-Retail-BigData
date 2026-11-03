"""Download and audit Kaggle jessekeats/convenience-store for a retail Hadoop project.
Run from the project root: python3 code/inspect_convenience_store.py
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import sqlite3
import zipfile
from collections import defaultdict
from pathlib import Path

DATASET = 'jessekeats/convenience-store'
KEYWORDS = {
    'Mã giao dịch': ['orderid', 'invoice', 'transactionid', 'basketid', 'receipt', 'billid', 'ticketid'],
    'Sản phẩm': ['product', 'item', 'sku', 'barcode', 'stockcode'],
    'Số lượng': ['quantity', 'qty', 'units', 'sold'],
    'Đơn giá / doanh thu': ['price', 'amount', 'total', 'revenue', 'salesvalue', 'cost'],
    'Cửa hàng': ['store', 'branch', 'outlet', 'shop'],
    'Ngày giờ': ['date', 'time', 'timestamp', 'day'],
    'Khách hàng': ['customer', 'member', 'household', 'client'],
}


def normalized(name: str) -> str:
    return ''.join(c for c in name.lower() if c.isalnum())


def matches(columns: list[str], category: str) -> list[str]:
    return [c for c in columns if any(x in normalized(c) for x in KEYWORDS[category])]


def audit_rows(rows, origin: str, limit: int):
    iterator = iter(rows)
    try:
        headers = [str(x).strip().lstrip('\ufeff') for x in next(iterator)]
    except StopIteration:
        return {'name': origin, 'columns': [], 'count': 0, 'complete': True}
    scanned, samples = 0, []
    basket_ids = defaultdict(set)
    order_cols = matches(headers, 'Mã giao dịch')
    item_cols = matches(headers, 'Sản phẩm')
    order_i = headers.index(order_cols[0]) if order_cols else None
    item_i = headers.index(item_cols[0]) if item_cols else None
    for row in iterator:
        if not row or not any(str(x).strip() for x in row):
            continue
        scanned += 1
        if len(samples) < 3:
            samples.append(dict(zip(headers, [str(v)[:80] for v in row])))
        if order_i is not None and item_i is not None and len(row) > max(order_i, item_i):
            basket_ids[str(row[order_i])].add(str(row[item_i]))
        if scanned >= limit:
            break
    return {
        'name': origin, 'columns': headers, 'count': scanned,
        'complete': scanned < limit, 'samples': samples,
        'multi_product_orders_in_sample': sum(len(v) >= 2 for v in basket_ids.values()),
        'distinct_order_ids_in_sample': len(basket_ids),
    }


def audit_text(path: Path, limit: int):
    opening = gzip.open if path.name.lower().endswith('.gz') else open
    with opening(path, 'rt', encoding='utf-8-sig', errors='replace', newline='') as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            delimiter = csv.Sniffer().sniff(sample, delimiters=',;\t|').delimiter
        except csv.Error:
            delimiter = '\t' if '.tsv' in path.name.lower() else ','
        return audit_rows(csv.reader(f, delimiter=delimiter), path.name, limit)


def audit_sqlite(path: Path):
    items = []
    db = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
    try:
        for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
            escaped = name.replace('"', '""')
            cols = [r[1] for r in db.execute(f'PRAGMA table_info("{escaped}")')]
            count = db.execute(f'SELECT COUNT(*) FROM "{escaped}"').fetchone()[0]
            items.append({'name': f'{path.name} → {name}', 'columns': cols, 'count': count, 'complete': True, 'samples': []})
    finally:
        db.close()
    return items


def inspect_file(path: Path, limit: int):
    suffix = path.suffix.lower()
    if suffix in {'.csv', '.tsv', '.txt'} or path.name.lower().endswith(('.csv.gz', '.tsv.gz')):
        return [audit_text(path, limit)]
    if suffix in {'.db', '.sqlite', '.sqlite3'}:
        return audit_sqlite(path)
    if suffix == '.xlsx':
        try:
            from openpyxl import load_workbook
        except ImportError:
            return [{'name': path.name, 'note': 'Cần cài openpyxl để đọc file Excel.'}]
        wb = load_workbook(path, read_only=True, data_only=True)
        try:
            return [audit_rows(ws.iter_rows(values_only=True), f'{path.name} → {ws.title}', limit) for ws in wb.worksheets]
        finally:
            wb.close()
    if suffix == '.parquet':
        try:
            import pyarrow.parquet as pq
            pf = pq.ParquetFile(path)
            return [{'name': path.name, 'columns': pf.schema.names, 'count': pf.metadata.num_rows, 'complete': True, 'samples': []}]
        except ImportError:
            return [{'name': path.name, 'note': 'Cần cài pyarrow để đọc file Parquet.'}]
    if suffix == '.zip':
        items = []
        with zipfile.ZipFile(path) as zf:
            for member in zf.infolist():
                if member.is_dir():
                    continue
                filename = member.filename.lower()
                if filename.endswith(('.csv', '.tsv')):
                    with zf.open(member) as raw, io.TextIOWrapper(raw, encoding='utf-8-sig', errors='replace', newline='') as f:
                        delimiter = '\t' if filename.endswith('.tsv') else ','
                        items.append(audit_rows(csv.reader(f, delimiter=delimiter), f'{path.name} → {member.filename}', limit))
                else:
                    items.append({'name': f'{path.name} → {member.filename}', 'note': f'File trong ZIP, {member.file_size:,} bytes; chưa tự động đọc.'})
        return items
    return [{'name': path.name, 'note': 'Chưa tự động đọc định dạng này.'}]


def make_report(root: Path, entries: list[dict], files: list[Path], limit: int):
    lines = [
        '# Kiểm tra bộ dữ liệu Kaggle: Convenience Store', '',
        f'- Nguồn: https://www.kaggle.com/datasets/{DATASET}',
        '- Dữ liệu gốc: giữ nguyên trong `data/raw/kaggle_convenience_store/`',
        f'- Giới hạn đọc mỗi file dữ liệu: {limit:,} dòng (nếu đạt giới hạn thì không phải tổng số dòng).', '',
        '## Danh sách file', '',
    ]
    for path in files:
        lines.append(f'- `{path.relative_to(root)}` — {path.stat().st_size / 1048576:.2f} MiB')
    lines += ['', '## Cấu trúc dữ liệu', '']
    all_cols = []
    for d in entries:
        lines.append(f"### {d['name']}")
        if d.get('note'):
            lines.extend([d['note'], ''])
            continue
        cols = d['columns']
        all_cols.extend(cols)
        count_note = 'đầy đủ' if d['complete'] else 'đã đọc đến giới hạn, chưa phải tổng số dòng'
        lines.extend([
            f"- Số dòng: **{d['count']:,}** ({count_note}).",
            f"- Số cột: **{len(cols)}**.",
            '- Các cột: ' + (', '.join(f'`{c}`' for c in cols) or 'Không xác định'),
        ])
        for cat in KEYWORDS:
            found = matches(cols, cat)
            if found:
                lines.append(f"- {cat}: {', '.join(f'`{c}`' for c in found)}")
        if d.get('distinct_order_ids_in_sample'):
            lines.append(f"- Kiểm tra giỏ hàng trong mẫu: {d['multi_product_orders_in_sample']:,} mã giao dịch chứa ít nhất 2 giá trị sản phẩm khác nhau, trên {d['distinct_order_ids_in_sample']:,} mã giao dịch.")
        if d.get('samples'):
            lines.extend(['- Một số bản ghi đầu:', '```json'])
            lines += [json.dumps(x, ensure_ascii=False, default=str) for x in d['samples']]
            lines.append('```')
        lines.append('')
    lines += ['## Đối chiếu sơ bộ đề cương', '']
    for cat in KEYWORDS:
        found = matches(sorted(set(all_cols)), cat)
        lines.append(f"- **{cat}:** " + (', '.join(f'`{x}`' for x in found) if found else 'Chưa phát hiện cột tương ứng'))
    lines += [
        '', '**Cảnh báo:** Tên cột chỉ giúp phát hiện sơ bộ. Cần kiểm tra khóa và quan hệ giữa các bảng, tính hợp lệ của số tiền, mã giao dịch, và chất lượng dữ liệu trước khi thiết kế Star Schema.',
        'Sự tồn tại của mã giao dịch và mã sản phẩm không tự động chứng minh có giỏ hàng nhiều sản phẩm.',
    ]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--local', action='store_true', help='Chỉ kiểm tra dữ liệu có sẵn; không tải từ Kaggle')
    parser.add_argument('--limit', type=int, default=50000, help='Số dòng tối đa đọc mỗi bảng/file (mặc định 50000)')
    args = parser.parse_args()
    if args.limit < 1:
        parser.error('--limit phải lớn hơn 0')
    root = Path.cwd()
    data_dir = root / 'data' / 'raw' / 'kaggle_convenience_store'
    report = root / 'docs' / 'dataset_audit.md'
    data_dir.mkdir(parents=True, exist_ok=True)
    files = [p for p in data_dir.rglob('*') if p.is_file()]
    if not files and not args.local:
        try:
            import kagglehub
        except ImportError:
            raise SystemExit('Thiếu kagglehub. Cài trong .venv: python -m pip install kagglehub==1.0.2')
        print('Đang tải dataset công khai từ Kaggle:', DATASET)
        try:
            kagglehub.dataset_download(DATASET, output_dir=str(data_dir))
        except Exception as exc:
            raise SystemExit(f'Không tải được dataset: {exc}\nNếu Kaggle yêu cầu quyền truy cập, hãy đăng nhập Kaggle trên máy của bạn.')
        files = [p for p in data_dir.rglob('*') if p.is_file()]
    if not files:
        raise SystemExit(f'Không thấy file dữ liệu trong: {data_dir}')
    files.sort()
    entries = []
    for file in files:
        print('Đang khảo sát:', file.relative_to(root))
        try:
            entries.extend(inspect_file(file, args.limit))
        except Exception as exc:
            entries.append({'name': file.name, 'note': f'Không đọc được: {type(exc).__name__}: {exc}'})
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(make_report(root, entries, files, args.limit), encoding='utf-8')
    print(f'\nĐã tạo báo cáo: {report}')
    print(f'Có {len(files)} file, {len(entries)} bảng/đối tượng được khảo sát.')
    print('Mở docs/dataset_audit.md trong VS Code để xem kết quả.')


if __name__ == '__main__':
    main()
