"""
track.py  -  Phase B: normalize raw analyzer output and follow every finding
across consecutive analysed commits (issue-history tracker).

Input : data/raw/<repo>/<NNN_hash>/{meta.json, semgrep.json, sonar_issues.json}
        repos/<repo>  (git clone, used for code context + rename detection)
Output: data/derived/findings.csv        one row per finding per snapshot
        data/derived/issue_histories.csv one row per tracked issue (lifetime table)
        data/derived/match_log.csv       every matching decision (method / ambiguity)
        data/derived/snapshots.csv       one row per analysed commit (LOC, counts)

Matching strategy (applied between snapshot k-1 and k, same repo, same tool):
  0. paths are mapped through git rename detection (git diff -M) between the two commits
  1. EXACT   : rule + path + normalized code of the flagged line(s) + occurrence index
  2. CONTEXT : rule + path + normalized code (line moved or duplicated code reordered)
  3. MESSAGE : rule + path + message, nearest line (code on the line was edited)
  Anything else is 'introduced' (new) / 'removed' (old). Several equally good candidates
  are logged as AMBIGUOUS in match_log.csv instead of being silently forced.
Independent check: SonarQube's own issue key (sonar_key) is kept so our tracker can be
compared against SonarQube's internal tracking (validate.py).
"""
import csv, json, re, subprocess, sys
from collections import defaultdict
from datetime import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHASE = sys.argv[1] if len(sys.argv) > 1 else ""   # e.g. "phaseC"; empty = pilot
SFX = ("_" + PHASE) if PHASE else ""
RAW = ROOT / "data" / ("raw" + SFX)
REPOS = ROOT / "repos"
OUT = ROOT / "data" / ("derived" + SFX)
OUT.mkdir(parents=True, exist_ok=True)

# Generated / vendored code is not developer-written source: excluded for BOTH groups.
# (Rule added after the pilot showed a committed 'build/' copy of the package in dhSegment.)
EXCLUDE_PATH = re.compile(r"(^|/)(build|dist|\.eggs|[^/]*\.egg-info|venv|\.venv|env|site-packages|node_modules|third_party|vendor)/")

SEMGREP_CAT = {"security": "security", "correctness": "reliability",
               "best-practice": "maintainability", "maintainability": "maintainability",
               "performance": "maintainability", "portability": "maintainability"}
SONAR_Q = {"SECURITY": "security", "RELIABILITY": "reliability", "MAINTAINABILITY": "maintainability"}
SONAR_TYPE = {"VULNERABILITY": "security", "BUG": "reliability", "CODE_SMELL": "maintainability",
              "SECURITY_HOTSPOT": "security"}


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


class Source:
    """Caches file contents at a given commit (git show commit:path)."""
    def __init__(self, repo):
        self.repo, self.cache = repo, {}

    def lines(self, commit, path):
        k = (commit, path)
        if k not in self.cache:
            self.cache[k] = git(self.repo, "show", f"{commit}:{path}").splitlines()
        return self.cache[k]


def norm_code(s):
    s = re.sub(r"#.*$", "", s)                  # drop trailing comments
    return re.sub(r"\s+", "", s)                # whitespace-insensitive


def norm_rule(check_id):
    return re.sub(r"^.*?(semgrep_[A-Za-z0-9_-]+\.|rules\.)", "", check_id, count=1)


def rel_path(p, repo_name):
    p = p.replace("\\", "/")
    marker = f"repos/{repo_name}/"
    i = p.find(marker)
    return p[i + len(marker):] if i >= 0 else p.lstrip("./")


def load_snapshot(cdir, repo_name, src):
    meta = json.loads((cdir / "meta.json").read_text(encoding="utf-8"))
    h = meta["commit"]
    rows = []
    sg = cdir / "semgrep.json"
    if sg.exists():
        seen = set()
        for r in json.loads(sg.read_text(encoding="utf-8")).get("results", []):
            md = r["extra"].get("metadata", {}) or {}
            path = rel_path(r["path"], repo_name)
            rule = norm_rule(r["check_id"])
            key = (rule, path, r["start"]["line"], r["start"]["col"])
            if key in seen:           # same rule in both rulesets
                continue
            seen.add(key)
            cat = SEMGREP_CAT.get(str(md.get("category", "")).lower(), "maintainability")
            cwe = md.get("cwe")
            rows.append({"tool": "semgrep", "rule": rule, "category": cat,
                         "severity": r["extra"].get("severity", ""),
                         "path": path, "line": r["start"]["line"], "end_line": r["end"]["line"],
                         "message": r["extra"].get("message", "").strip()[:300],
                         "cwe": "; ".join(cwe) if isinstance(cwe, list) else (cwe or ""),
                         "sonar_key": ""})
    sq = cdir / "sonar_issues.json"
    if sq.exists():
        for i in json.loads(sq.read_text(encoding="utf-8")):
            path = i["component"].split(":", 1)[1] if ":" in i["component"] else i["component"]
            tr = i.get("textRange") or {}
            imp = i.get("impacts") or []
            if imp:
                order = {"HIGH": 3, "BLOCKER": 4, "MEDIUM": 2, "LOW": 1, "INFO": 0}
                top = max(imp, key=lambda x: order.get(x.get("severity", ""), 0))
                cat, sev = SONAR_Q.get(top["softwareQuality"], "maintainability"), top.get("severity", "")
            else:
                cat, sev = SONAR_TYPE.get(i.get("type", ""), "maintainability"), i.get("severity", "")
            rows.append({"tool": "sonarqube", "rule": i["rule"], "category": cat, "severity": sev,
                         "path": path, "line": i.get("line") or tr.get("startLine") or 0,
                         "end_line": tr.get("endLine") or i.get("line") or 0,
                         "message": (i.get("message") or "").strip()[:300], "cwe": "",
                         "sonar_key": i["key"]})
    rows = [r for r in rows if not EXCLUDE_PATH.search(r["path"])]
    for r in rows:
        ls = src.lines(h, r["path"])
        a, b = max(1, int(r["line"])), max(int(r["line"]), int(r["end_line"]))
        b = min(b, a + 5)
        r["code"] = norm_code(" ".join(ls[a - 1:b])) if ls and a <= len(ls) else ""
    avail = {t for t, f in (("semgrep", sg), ("sonarqube", sq)) if f.exists()}
    return meta, rows, avail


def renames(repo, old, new):
    m = {}
    for line in git(repo, "diff", "-M", "--name-status", old, new).splitlines():
        parts = line.split("\t")
        if parts[0].startswith("R") and len(parts) == 3:
            m[parts[1]] = parts[2]
    return m


def existing_files(repo, commit):
    return set(git(repo, "ls-tree", "-r", "--name-only", commit).splitlines())


MAX_SHIFT = 15   # max distance (after diff-based line mapping) for CONTEXT/MESSAGE matches


def make_line_mapper(src, old_commit, new_commit):
    """Translate an old line number into the new file's coordinates using a line diff,
    so that 'nearest line' comparisons are not fooled by code inserted above the issue."""
    import difflib
    cache = {}

    def mapper(old_path, new_path, line):
        k = (old_path, new_path)
        if k not in cache:
            a, b = src.lines(old_commit, old_path), src.lines(new_commit, new_path)
            ops = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
            cache[k] = ops
        for tag, i1, i2, j1, j2 in cache[k]:
            if i1 <= line - 1 < i2 or (i1 == i2 == line - 1):
                if tag == "equal":
                    return j1 + (line - 1 - i1) + 1
                return j1 + min(line - 1 - i1, max(0, j2 - j1 - 1)) + 1
        return line
    return mapper


def match(prev, cur, ren, log, ctx, mapper=None):
    """prev/cur: lists of finding dicts (same tool). Returns {cur_idx: prev_idx}."""
    mapping, used_p, used_c = {}, set(), set()

    def ppath(f):
        return ren.get(f["path"], f["path"])

    def occ_key(lst, fn):
        cnt, out = defaultdict(int), []
        for f in sorted(lst, key=lambda x: (x["path"], x["line"])):
            k = fn(f); out.append((k + (cnt[k],), f)); cnt[k] += 1
        return out

    # 1 EXACT (with occurrence index)
    pk = {k: f["_i"] for k, f in occ_key(prev, lambda f: (f["rule"], ppath(f), f["code"]))}
    for k, f in occ_key(cur, lambda f: (f["rule"], f["path"], f["code"])):
        if k in pk and pk[k] not in used_p and f["code"]:
            mapping[f["_i"]] = pk[k]; used_p.add(pk[k]); used_c.add(f["_i"])
            log.append({**ctx, "method": "exact", "cur": f["_i"], "prev": pk[k], "ambiguous": False})

    # 2 CONTEXT + 3 MESSAGE, nearest line, flag ties
    for method, keyf in (("context", lambda f: (f["rule"], f["code"])),
                         ("message", lambda f: (f["rule"], f["message"]))):
        pool = defaultdict(list)
        for f in prev:
            if f["_i"] not in used_p:
                pool[(ppath(f),) + keyf(f)].append(f)
        for f in sorted(cur, key=lambda x: x["line"]):
            if f["_i"] in used_c or (method == "context" and not f["code"]):
                continue
            cands = [p for p in pool.get((f["path"],) + keyf(f), []) if p["_i"] not in used_p]
            if not cands:
                continue
            def dist(p):
                ml = mapper(p["path"], f["path"], p["line"]) if mapper else p["line"]
                return abs(ml - f["line"])
            cands = [p for p in cands if dist(p) <= MAX_SHIFT]
            if not cands:
                continue
            cands.sort(key=dist)
            amb = len(cands) > 1 and dist(cands[0]) == dist(cands[1])
            best = cands[0]
            mapping[f["_i"]] = best["_i"]; used_p.add(best["_i"]); used_c.add(f["_i"])
            log.append({**ctx, "method": method, "cur": f["_i"], "prev": best["_i"], "ambiguous": amb})
    return mapping


def track_repo(rdir_raw):
    name = rdir_raw.name
    repo = REPOS / name
    if not repo.exists():
        full = name.replace("__", "/")
        subprocess.run(["git", "clone", "--quiet", f"https://github.com/{full}.git", str(repo)], check=True)
    src = Source(repo)
    snaps = sorted(d for d in rdir_raw.iterdir() if d.is_dir() and (d / "meta.json").exists())
    all_findings, histories, mlog, snap_rows = [], [], [], []
    counter = 0
    prev_meta = None
    prev_by_tool = {}
    last_commit = {}          # tool -> last commit on which that tool produced output
    for k, cdir in enumerate(snaps):
        meta, rows, avail = load_snapshot(cdir, name, src)
        h, date = meta["commit"], meta["committer_date"]
        files_now = existing_files(repo, h)
        ren = renames(repo, prev_meta["commit"], h) if prev_meta else {}
        snap_rows.append({"repo": meta["repo"], "group": meta["group"], "index": k + 1, "commit": h,
                          "date": date, "py_loc": sum(sum(1 for l in src.lines(h, f) if l.strip()) for f in files_now
                                        if f.endswith(".py") and not EXCLUDE_PATH.search(f)),
                          "py_loc_scanner_all": meta["py_loc_nonblank"], "py_files": meta["py_files"],
                          "errors": "; ".join(meta.get("errors", [])), "missing_tools": "",
                          **{f"n_{t}": sum(r["tool"] == t for r in rows) for t in ("semgrep", "sonarqube")}})
        by_tool = defaultdict(list)
        for i, r in enumerate(rows):
            r["_i"] = i
            by_tool[r["tool"]].append(r)
        for tool in ("semgrep", "sonarqube"):
            if tool not in avail:          # analyzer failed on this commit: bridge the gap
                by_tool[tool] = prev_by_tool.get(tool, [])
                snap_rows[-1]["missing_tools"] = snap_rows[-1].get("missing_tools", "") + tool + " "
                continue
            cur = by_tool.get(tool, [])
            prev = prev_by_tool.get(tool, [])
            ctx = {"repo": meta["repo"], "tool": tool, "snapshot": k + 1}
            lc = last_commit.get(tool)
            ren_t = renames(repo, lc, h) if (lc and prev_meta and lc != prev_meta["commit"]) else ren
            mp = match(prev, cur, ren_t, mlog, ctx, make_line_mapper(src, lc, h)) if lc else {}
            last_commit[tool] = h
            prev_idx = {p["_i"]: p for p in prev}
            matched_prev = set(mp.values())
            # removed
            for p in prev:
                if p["_i"] in matched_prev:
                    continue
                hist = histories[p["issue_id"]]
                newpath = ren_t.get(p["path"], p["path"])
                if newpath not in files_now:
                    mech = "file_deleted"
                else:
                    code_now = {norm_code(l) for l in src.lines(h, newpath)}
                    mech = "code_still_present" if p["code"] and p["code"] in code_now else "code_changed"
                hist.update({"removed_commit": h, "removed_date": date, "removed_snapshot": k + 1,
                             "removal_mechanism": mech, "censored": False})
            # continuing / introduced
            for f in cur:
                if f["_i"] in mp:
                    f["issue_id"] = prev_idx[mp[f["_i"]]]["issue_id"]
                    hist = histories[f["issue_id"]]
                    hist["last_seen_snapshot"] = k + 1
                    if f["path"] != hist["path_last"]:
                        hist["moved"] = True
                    hist["path_last"] = f["path"]
                    if f["sonar_key"] and f["sonar_key"] not in hist["sonar_keys"]:
                        hist["sonar_keys"] += ("|" if hist["sonar_keys"] else "") + f["sonar_key"]
                else:
                    f["issue_id"] = counter; counter += 1
                    histories.append({
                        "issue_id": f["issue_id"], "repo": meta["repo"], "group": meta["group"],
                        "tool": tool, "rule": f["rule"], "category": f["category"], "severity": f["severity"],
                        "cwe": f["cwe"], "path_first": f["path"], "path_last": f["path"], "line_first": f["line"],
                        "message": f["message"],
                        "present_at_first_snapshot": lc is None,
                        "introduced_commit": h, "introduced_date": date, "introduced_snapshot": k + 1,
                        "last_seen_snapshot": k + 1, "removed_commit": "", "removed_date": "",
                        "removed_snapshot": "", "removal_mechanism": "", "censored": True,
                        "moved": False, "sonar_keys": f["sonar_key"]})
                all_findings.append({"repo": meta["repo"], "group": meta["group"], "snapshot": k + 1,
                                     "commit": h, "date": date, "issue_id": f["issue_id"],
                                     **{c: f[c] for c in ("tool", "rule", "category", "severity", "path",
                                                          "line", "message", "cwe", "sonar_key", "code")}})
        prev_by_tool = by_tool
        prev_meta = meta
    # lifetimes
    end_date = snap_rows[-1]["date"]
    n = len(snap_rows)
    for hst in histories:
        t0 = datetime.fromisoformat(hst["introduced_date"])
        t1 = datetime.fromisoformat(hst["removed_date"] or end_date)
        hst["lifetime_days"] = round((t1 - t0).total_seconds() / 86400, 3)
        hst["lifetime_snapshots"] = (hst["removed_snapshot"] or n + 1) - hst["introduced_snapshot"] \
            if hst["removed_snapshot"] else n - hst["introduced_snapshot"]
        hst["observation_end_date"] = end_date
    for m in mlog:
        m["repo_dir"] = name
    return all_findings, histories, mlog, snap_rows


def write(path, rows):
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    print(f"  wrote {path.relative_to(ROOT)} ({len(rows)} rows)")


if __name__ == "__main__":
    F, H, M, S = [], [], [], []
    offset = 0
    for rdir in sorted(d for d in RAW.iterdir() if d.is_dir()):
        print(f"Tracking {rdir.name} ...")
        f, h, m, s = track_repo(rdir)
        for x in h: x["issue_id"] += offset
        for x in f: x["issue_id"] += offset
        offset += len(h)
        F += f; H += h; M += m; S += s
    write(OUT / "findings.csv", F)
    write(OUT / "issue_histories.csv", H)
    write(OUT / "match_log.csv", M)
    write(OUT / "snapshots.csv", S)
