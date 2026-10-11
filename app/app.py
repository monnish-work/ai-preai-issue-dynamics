"""
Issue Lifelines - web app for the study "Issue Dynamics in AI-Assisted vs. Pre-AI Software".

Run:  python app/app.py        then open http://localhost:5000
The data comes from app/study.db (build it with: python app/database.py).
"""
import json
import secrets
import re
import sqlite3
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path

from flask import Flask, g, jsonify, render_template, request, session

import stats

HERE = Path(__file__).resolve().parent
DB = HERE / "study.db"
KEY_FILE = HERE / ".secret_key"

app = Flask(__name__, static_folder="static", template_folder="templates")
if not KEY_FILE.exists():
    KEY_FILE.write_text(secrets.token_hex(32))
app.secret_key = KEY_FILE.read_text().strip()
app.config["JSON_SORT_KEYS"] = False

CATS = ["maintainability", "reliability", "security"]


# ------------------------------------------------------------------ db helpers
def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_):
    d = g.pop("db", None)
    if d is not None:
        d.close()


def rows(sql, *args):
    return [dict(r) for r in db().execute(sql, args).fetchall()]


def table(phase, name):
    r = db().execute("SELECT body FROM tables_json WHERE phase=? AND name=?", (phase, name)).fetchone()
    return json.loads(r["body"]) if r else []


def now():
    return datetime.now().isoformat(timespec="seconds")


# ------------------------------------------------------------------ auth (name only)
@app.post("/api/login")
def login():
    name = (request.json or {}).get("name", "").strip()[:60]
    if len(name) < 2:
        return jsonify(error="Enter at least 2 characters."), 400
    d = db()
    if d.execute("SELECT 1 FROM users WHERE name=?", (name,)).fetchone():
        d.execute("UPDATE users SET last_seen=?, visits=visits+1 WHERE name=?", (now(), name))
    else:
        d.execute("INSERT INTO users VALUES (?,?,?,1)", (name, now(), now()))
    d.commit()
    session["name"] = name
    return jsonify(name=name)


@app.post("/api/logout")
def logout():
    session.pop("name", None)
    return jsonify(ok=True)


@app.get("/api/me")
def me():
    n = session.get("name")
    if not n:
        return jsonify(name=None)
    u = db().execute("SELECT * FROM users WHERE name=?", (n,)).fetchone()
    return jsonify(name=n, visits=u["visits"] if u else 1)


# ------------------------------------------------------------------ project summaries
def project_summary(phase, repo):
    p = rows("SELECT * FROM projects WHERE phase=? AND repo=?", phase, repo)
    if not p:
        return None
    p = p[0]
    snaps = rows("SELECT idx, sha, date, loc, maint, rel, sec, missing FROM snapshots WHERE phase=? AND repo=? ORDER BY idx",
                 phase, repo)
    iss = rows("SELECT category, baseline, removed_idx, mechanism, life_days, life_commits, rule, message FROM issues "
               "WHERE phase=? AND repo=?", phase, repo)
    kloc = sum(s["loc"] for s in snaps) / len(snaps) / 1000 if snaps else 0
    per = {}
    for c in CATS + ["all"]:
        sub = [i for i in iss if c == "all" or i["category"] == c]
        intro = sum(1 for i in sub if not i["baseline"])
        rem = sum(1 for i in sub if i["removed_idx"] is not None)
        base = sum(1 for i in sub if i["baseline"])
        per[c] = {"baseline": base, "introduced": intro, "removed": rem,
                  "open_end": len(sub) - rem,
                  "intro_per_kloc": round(intro / kloc, 2) if kloc else None,
                  "removed_per_kloc": round(rem / kloc, 2) if kloc else None,
                  "remediation_share": round(rem / (base + intro), 3) if base + intro else None}
    last = snaps[-1] if snaps else {}
    ok = [s for s in snaps if "sonarqube" not in (s["missing"] or "")]
    p.update({"snapshots": len(snaps), "first_date": snaps[0]["date"][:10] if snaps else "",
              "last_date": last.get("date", "")[:10], "loc_first": snaps[0]["loc"] if snaps else 0,
              "loc_last": last.get("loc", 0), "mean_kloc": round(kloc, 2),
              "open_now": (ok[-1]["maint"] + ok[-1]["rel"] + ok[-1]["sec"]) if ok else 0,
              "rates": per})
    return p, snaps, iss


def km_block(iss, unit):
    col = "life_commits" if unit == "commits" else "life_days"
    out = {}
    for c in CATS + ["all"]:
        sub = [i for i in iss if not i["baseline"] and (c == "all" or i["category"] == c)]
        pts = stats.km([i[col] for i in sub], [i["removed_idx"] is not None for i in sub])
        out[c] = {"n": len(sub), "events": sum(i["removed_idx"] is not None for i in sub),
                  "median": stats.km_median(pts) if pts else None, "curve": pts}
    return out


@app.get("/api/meta")
def meta():
    phases = rows("SELECT * FROM phases")
    for ph in phases:
        ph["projects"] = []
        for p in rows("SELECT repo FROM projects WHERE phase=? ORDER BY grp, match_id, repo", ph["id"]):
            s, _, _ = project_summary(ph["id"], p["repo"])
            s.pop("rates", None)
            ph["projects"].append(s)
    v = db().execute("SELECT body FROM tables_json WHERE phase='all' AND name='versions'").fetchone()
    users = rows("SELECT name, visits, last_seen FROM users ORDER BY last_seen DESC LIMIT 8")
    return jsonify(phases=phases, versions=json.loads(v["body"]) if v else [], users=users)


@app.get("/api/compare")
def compare():
    phase, ai, hu = request.args.get("phase", "phaseC"), request.args.get("ai"), request.args.get("human")
    unit = request.args.get("unit", "commits")
    out, sets = {}, {}
    for key, repo in (("ai", ai), ("human", hu)):
        res = project_summary(phase, repo)
        if not res:
            return jsonify(error=f"Unknown project {repo}"), 404
        p, snaps, iss = res
        mech = Counter(i["mechanism"] for i in iss if i["removed_idx"] is not None)
        rules = Counter((i["rule"], i["category"]) for i in iss)
        msg = {}
        for i in iss:
            msg.setdefault(i["rule"], i["message"])
        p["series"] = snaps
        p["km"] = km_block(iss, unit)
        p["mechanisms"] = dict(mech)
        p["top_rules"] = [{"rule": r, "category": c, "n": n, "example": msg[r][:140]} for (r, c), n in rules.most_common(8)]
        out[key] = p
        sets[key] = iss
    col = "life_commits" if unit == "commits" else "life_days"
    tests = {}
    for c in CATS + ["all"]:
        a = [i for i in sets["ai"] if not i["baseline"] and (c == "all" or i["category"] == c)]
        b = [i for i in sets["human"] if not i["baseline"] and (c == "all" or i["category"] == c)]
        if a and b:
            chi, pv = stats.logrank([i[col] for i in a], [i["removed_idx"] is not None for i in a],
                                    [i[col] for i in b], [i["removed_idx"] is not None for i in b])
            tests[c] = {"chi2": chi, "p": pv}
    out["tests"] = tests
    out["unit"] = unit
    return jsonify(out)


@app.get("/api/results")
def results():
    """Group-level answers to RQ1-RQ3 for one phase."""
    phase = request.args.get("phase", "phaseC")
    unit = request.args.get("unit", "commits")
    iss = rows("SELECT grp, category, baseline, removed_idx, mechanism, life_days, life_commits FROM issues WHERE phase=?", phase)
    km = {g: km_block([i for i in iss if i["grp"] == g], unit) for g in ("AI", "PreAI")}
    col = "life_commits" if unit == "commits" else "life_days"
    tests = {}
    for c in CATS + ["all"]:
        a = [i for i in iss if i["grp"] == "AI" and not i["baseline"] and (c == "all" or i["category"] == c)]
        b = [i for i in iss if i["grp"] == "PreAI" and not i["baseline"] and (c == "all" or i["category"] == c)]
        if a and b:
            chi, pv = stats.logrank([i[col] for i in a], [i["removed_idx"] is not None for i in a],
                                    [i[col] for i in b], [i["removed_idx"] is not None for i in b])
            tests[c] = {"chi2": chi, "p": pv}
    mech = {}
    for g_ in ("AI", "PreAI"):
        m = Counter(i["mechanism"] for i in iss if i["grp"] == g_ and i["removed_idx"] is not None)
        mech[g_] = dict(m)
    rates = table(phase, "rates_by_repo")
    return jsonify(km=km, tests=tests, mechanisms=mech, rates=rates, unit=unit,
                   repo_tests=table(phase, "repo_level_tests"), repo_measures=table(phase, "repo_level_measures"),
                   rq3=table(phase, "rq3_security_vs_other"))


# ------------------------------------------------------------------ issues
@app.get("/api/issues")
def issues():
    a = request.args
    phase = a.get("phase", "phaseC")
    sql, args = "SELECT id, repo, grp, tool, rule, category, severity, message, path_last, intro_idx, last_idx, removed_idx, mechanism, baseline, life_commits, life_days FROM issues WHERE phase=?", [phase]
    if a.get("repo"):
        sql += " AND repo=?"; args.append(a["repo"])
    if a.get("group"):
        sql += " AND grp=?"; args.append(a["group"])
    if a.get("category"):
        sql += " AND category=?"; args.append(a["category"])
    st_ = a.get("status")
    if st_ == "open":
        sql += " AND removed_idx IS NULL"
    elif st_ == "removed":
        sql += " AND removed_idx IS NOT NULL"
    elif st_ in ("code_changed", "file_deleted", "code_still_present"):
        sql += " AND mechanism=?"; args.append(st_)
    if a.get("q"):
        sql += " AND (message LIKE ? OR rule LIKE ? OR path_last LIKE ?)"
        q = f"%{a['q']}%"; args += [q, q, q]
    order = {"longest": "life_commits DESC", "newest": "intro_idx DESC", "oldest": "intro_idx ASC"}.get(a.get("sort"), "repo, intro_idx")
    total = db().execute(f"SELECT COUNT(*) FROM ({sql})", args).fetchone()[0]
    page = max(1, int(a.get("page", 1)))
    items = rows(sql + f" ORDER BY {order} LIMIT 25 OFFSET {(page - 1) * 25}", *args)
    return jsonify(total=total, page=page, pages=max(1, -(-total // 25)), items=items)


@app.get("/api/issue/<phase>/<int:iid>")
def issue(phase, iid):
    r = rows("SELECT * FROM issues WHERE phase=? AND id=?", phase, iid)
    if not r:
        return jsonify(error="Issue not found"), 404
    r = r[0]
    r["lines"] = json.loads(r["lines"])
    r["paths"] = json.loads(r["paths"])
    r["snapshots"] = rows("SELECT idx, sha, date, missing FROM snapshots WHERE phase=? AND repo=? ORDER BY idx", phase, r["repo"])
    return jsonify(r)


# ------------------------------------------------------------------ validation
@app.get("/api/validation")
def validation():
    phase = request.args.get("phase", "phaseC")
    sample = table(phase, "manual_validation_sample")
    checks = {r["issue_id"]: r for r in rows("SELECT * FROM manual_checks WHERE phase=?", phase)}
    for s in sample:
        s["check"] = checks.get(int(s["issue_id"]))
    return jsonify(agreement=table(phase, "validation_sonar_agreement"),
                   methods=table(phase, "validation_match_methods"), sample=sample,
                   events=table(phase, "validation_event_agreement"),
                   reasons=table(phase, "validation_disagreement_reasons"))


@app.post("/api/manual/<phase>/<int:iid>")
def save_manual(phase, iid):
    if not session.get("name"):
        return jsonify(error="Sign in first."), 401
    b = request.json or {}
    vals = [b.get(k, "") if b.get(k, "") in ("Y", "N", "") else "" for k in ("intro", "persist", "removal")]
    db().execute("INSERT OR REPLACE INTO manual_checks VALUES (?,?,?,?,?,?,?,?)",
                 (phase, iid, *vals, (b.get("notes") or "")[:1000], session["name"], now()))
    db().commit()
    return jsonify(ok=True, saved=now())


REPOS = HERE.parent / "repos"
_norm = lambda t: re.sub(r"\s+", "", re.sub(r"#.*$", "", t))


@app.get("/api/code")
def code():
    """Return a few lines of a file at a given commit, read from the local clone in repos/."""
    a = request.args
    repo, sha, path = a.get("repo", ""), a.get("sha", ""), a.get("path", "")
    line = int(a.get("line", 1) or 1)
    if not re.fullmatch(r"[0-9a-fA-F]{6,40}", sha) or ".." in path or not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        return jsonify(error="Bad request"), 400
    d = REPOS / repo.replace("/", "__")
    if not d.exists():
        return jsonify(error="This repository is not cloned in the repos folder on this computer.")
    r = subprocess.run(["git", "show", f"{sha}:{path}"], cwd=d, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        return jsonify(missing=True, path=path)
    lines = r.stdout.splitlines()
    find = a.get("find")
    found = None
    if find:
        target = _norm(find)
        hits = [i + 1 for i, t in enumerate(lines) if target and _norm(t) == target]
        if hits:
            found = min(hits, key=lambda h: abs(h - line))
            line = found
    lo, hi = max(1, line - 5), min(len(lines), line + 5)
    return jsonify(start=lo, lines=lines[lo - 1:hi], focus=line, found=found, total=len(lines), path=path)


@app.get("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    if not DB.exists():
        import database
        database.build()
    print("\n  Issue Lifelines is running:  http://localhost:5000\n  Stop it with Ctrl+C\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
