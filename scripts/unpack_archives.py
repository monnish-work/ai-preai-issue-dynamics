"""unpack_archives.py - extracts the archived raw scan output and tracker output into data/ (needed only to re-run the
pipeline; the web app ships with its database). Usage: python scripts/unpack_archives.py"""
import lzma, shutil, tarfile, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
A, D = ROOT / "data" / "archives", ROOT / "data"
for f in sorted(A.glob("*.tar.xz")):
    print("extracting", f.name); tarfile.open(f).extractall(D, filter="data")
for f in sorted(A.glob("*.zip")):
    if f.name.startswith(("raw_pilot", "derived_pilot", "raw_main_study")):
        print("extracting", f.name); zipfile.ZipFile(f).extractall(D)
db = ROOT / "app" / "study.db"
if not db.exists() and (ROOT / "app" / "study.db.xz").exists():
    with lzma.open(ROOT / "app" / "study.db.xz") as s, open(db, "wb") as t:
        shutil.copyfileobj(s, t)
print("done")
