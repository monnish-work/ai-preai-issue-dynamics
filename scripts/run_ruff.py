"""
run_ruff.py - adds Performance Efficiency findings (Ruff PERF / perflint rules) to every analysed commit.

Follows the professor's replication package (Zenodo 21870905, static_analysis/snapshot/ruff/run_ruff.py):
    ruff check . --isolated --select PERF --output-format json
(--isolated = the repository's own Ruff configuration is ignored, so every repository is checked with
the same rules). Mapping: mappings/ruff_rule_attribute_mapping.csv (all PERF rules -> Performance Efficiency).

Usage:  python scripts/run_ruff.py phaseC [--ruff PATH]
Input : data/raw_<phase>/<repo>/<NNN_hash>/meta.json   (commit hash), repos/<repo> (git clone)
Output: data/raw_<phase>/<repo>/<NNN_hash>/ruff.json    (Ruff JSON output, paths relative to the repo)
        data/raw_<phase>/ruff_version.txt
Safe to re-run: snapshots that already have ruff.json are skipped.
"""
import argparse, io, json, shutil, subprocess, sys, tarfile, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("phase")
ap.add_argument("--ruff", default="ruff")
a = ap.parse_args()
RAW = ROOT / "data" / f"raw_{a.phase}"

ver = subprocess.run([a.ruff, "--version"], capture_output=True, text=True).stdout.strip()
(RAW / "ruff_version.txt").write_text(ver + "\n", encoding="utf-8")
print(ver)

total = 0
for rdir in sorted(d for d in RAW.iterdir() if d.is_dir()):
    repo = ROOT / "repos" / rdir.name
    for cdir in sorted(d for d in rdir.iterdir() if d.is_dir() and (d / "meta.json").exists()):
        out = cdir / "ruff.json"
        if out.exists():
            continue
        commit = json.loads((cdir / "meta.json").read_text(encoding="utf-8"))["commit"]
        tmp = Path(tempfile.mkdtemp(prefix="ruff_"))
        try:
            tar = subprocess.run(["git", "archive", commit], cwd=repo, capture_output=True, check=True).stdout
            try:
                tarfile.open(fileobj=io.BytesIO(tar)).extractall(tmp, filter="data")
            except tarfile.ReadError:      # commit with an empty tree (e.g. hanyas/sds 002): no files
                pass
            r = subprocess.run([a.ruff, "check", ".", "--isolated", "--select", "PERF", "--output-format", "json",
                                "--exit-zero", "--no-cache"], cwd=tmp, capture_output=True, text=True)
            res = json.loads(r.stdout or "[]")
            for f in res:
                f["filename"] = str(Path(f["filename"]).relative_to(tmp)).replace("\\", "/")
            out.write_text(json.dumps(res), encoding="utf-8")
            total += len(res)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    print(rdir.name, "done", flush=True)
print("PERF findings (all snapshots):", total)
