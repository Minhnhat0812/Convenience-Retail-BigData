from pathlib import Path
import shutil
import kagglehub

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data/raw/kaggle_convenience_store/convenience_store.csv"

folder = Path(kagglehub.dataset_download("jessekeats/convenience-store"))
files = list(folder.rglob("convenience_store.csv"))
if len(files) != 1:
    raise FileNotFoundError(f"Khong tim thay dung 1 file convenience_store.csv trong {folder}")

DEST.parent.mkdir(parents=True, exist_ok=True)
if files[0].resolve() != DEST.resolve():
    shutil.copy2(files[0], DEST)
print(f"Da tai: {DEST}")
