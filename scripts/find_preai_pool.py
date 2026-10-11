"""
find_preai_pool.py  -  Phase C: a wider PreAI candidate pool, stratified by popularity,
so each AI repository can be matched on size (LOC) and popularity (stars).

The pilot query sorted by stars returned only 359-499-star repos (popularity bias).
Here we query several star bands separately and sort by last update.
Output: data/candidates/preai_pool_stratified.csv (+ queries appended to search_log_phaseC.json)
Needs GITHUB_TOKEN (same as find_candidates.py).
"""
import csv, json, os, re, sys, time
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "candidates"
TOKEN = os.environ.get("GITHUB_TOKEN", "").strip() or sys.exit("GITHUB_TOKEN is not set")
S = requests.Session()
S.headers.update({"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json",
                  "User-Agent": "ai-preai-issue-dynamics-study"})
EXCLUDE = re.compile(r"tutorial|homework|assignment|course|exercise|lesson|leetcode|awesome|"
                     r"benchmark|dataset|example|demo|template|boilerplate|playground|practice|learn|bootcamp|"
                     r"paper|implementation of|reimplementation|code for|official", re.I)
BANDS = ["10..30", "31..100", "101..300"]
SIZES = ["300..3000", "3001..15000", "15001..40000"]
log = {"run": datetime.now(timezone.utc).isoformat(), "queries": []}
rows, seen = [], set()
for stars in BANDS:
    for size in SIZES:
        q = (f"language:Python fork:false archived:false stars:{stars} size:{size} "
             f"created:2015-01-01..2020-06-30 pushed:2019-01-01..2021-12-31")
        kept = 0
        for page in range(1, 4):
            r = S.get("https://api.github.com/search/repositories",
                      params={"q": q, "per_page": 100, "page": page, "sort": "updated", "order": "desc"},
                      timeout=60)
            if r.status_code != 200:
                print("  HTTP", r.status_code, r.text[:120]); time.sleep(30); continue
            items = r.json().get("items", [])
            for it in items:
                desc = it.get("description") or ""
                if it["full_name"] in seen or EXCLUDE.search(it["full_name"] + " " + desc):
                    continue
                seen.add(it["full_name"]); kept += 1
                rows.append({"repo": it["full_name"], "url": it["html_url"], "stars": it["stargazers_count"],
                             "forks": it["forks_count"], "size_kb": it["size"],
                             "created_at": it["created_at"][:10], "pushed_at": it["pushed_at"][:10],
                             "open_issues": it["open_issues_count"], "has_license": bool(it.get("license")),
                             "description": desc[:200], "stars_band": stars, "size_band": size})
            time.sleep(2.2)
            if len(items) < 100:
                break
        log["queries"].append({"q": q, "sort": "updated", "kept": kept})
        print(f"  stars {stars:9} size {size:13} kept {kept}")
with open(OUT / "preai_pool_stratified.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
(OUT / "search_log_phaseC.json").write_text(json.dumps(log, indent=2))
print(f"DONE: {len(rows)} PreAI candidates -> data/candidates/preai_pool_stratified.csv")
