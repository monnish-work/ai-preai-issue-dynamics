"""
scan_repos.py  -  clone repos, pick commits, run Semgrep + SonarQube on every
selected commit, and archive the RAW analyzer output (brief Phase A, steps 13-16).

Usage (inside the ai_study folder, after  . .\\env.ps1 ):
    python scripts\\scan_repos.py                       # uses data\\study_repos.csv
    python scripts\\scan_repos.py --repos data\\x.csv --n 30 --mode last

Commit-selection rule (same for AI and PreAI, never changed between groups):
    --mode last    : the last N non-merge commits on the default branch (pilot default)
    --mode spread  : N non-merge commits evenly spaced over the whole history

Safe to re-run: commits already scanned are skipped (resume after a crash/sleep).
Everything is written inside the ai_study folder.
"""
import argparse, csv, hashlib, json, os, secrets, shutil, string, subprocess, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
REPOS = ROOT / "repos"
RAW = ROOT / "data" / "raw"
RULES = ROOT / "rules"
SONAR = "http://localhost:9000"
CRED = TOOLS / "sonar_credentials.json"      # local only, never shared

# SEMGREP_CMD lets run_extension_scan.ps1 call "python -m semgrep" when Windows blocks the semgrep.exe launcher
SEMGREP_CMD = os.environ.get("SEMGREP_CMD", "semgrep").split("|")
SEMGREP_RULESETS = ["p/python", "p/security-audit"]   # frozen to local files on first run


def log(msg):
    line = f"[{datetime.now():%H:%M:%S}] {msg}"
    print(line, flush=True)
    with open(ROOT / "data" / "scan_log.txt", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(cmd, cwd=None, check=True, timeout=3600):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed ({r.returncode}): {r.stderr[-1500:]}")
    return r


# Git LFS is not installed: check out LFS pointer files as they are (LFS content is never Python source)
NO_LFS = ["-c", "filter.lfs.process=", "-c", "filter.lfs.smudge=", "-c", "filter.lfs.clean=", "-c", "filter.lfs.required=false",
          "-c", "core.protectNTFS=false"]   # paths Windows cannot create are excluded by the sparse-checkout patterns below


def git(repo_dir, *args, check=True):
    return run(["git", *NO_LFS, *args], cwd=repo_dir, check=check).stdout


# --------------------------------------------------------------- Semgrep rules
def freeze_semgrep_rules():
    RULES.mkdir(exist_ok=True)
    paths = []
    for rs in SEMGREP_RULESETS:
        p = RULES / ("semgrep_" + rs.replace("p/", "").replace("/", "_") + ".yml")
        if not p.exists():
            log(f"Downloading Semgrep ruleset {rs} once (frozen for the whole study)")
            r = requests.get(f"https://semgrep.dev/c/{rs}", timeout=120)
            r.raise_for_status()
            p.write_text(r.text, encoding="utf-8")
            (RULES / (p.name + ".sha256")).write_text(hashlib.sha256(r.content).hexdigest())
        paths.append(p)
    return paths


# --------------------------------------------------------------- SonarQube
def sonar_up():
    try:
        return requests.get(f"{SONAR}/api/system/status", timeout=5).json().get("status") == "UP"
    except Exception:
        return False


def ensure_sonar():
    if sonar_up():
        return
    env = os.environ.copy()
    if os.name == "nt":
        bats = [p for p in (TOOLS / "sonarqube").rglob("StartSonar.bat") if "windows-x86-64" in str(p)]
        if not bats:
            sys.exit("SonarQube not found - run setup.ps1 first.")
        log("Starting SonarQube in a new window (1-3 minutes). Do NOT close that window.")
        subprocess.Popen(["cmd", "/c", "start", "SonarQube - keep open", str(bats[0])], env=env)
    else:   # macOS / Linux: tools/sonarqube/<version>/bin/<platform>/sonar.sh (installed by setup_mac.sh --with-scanners)
        plat = "macosx-universal-64" if sys.platform == "darwin" else "linux-x86-64"
        sh = [p for p in (TOOLS / "sonarqube").rglob("sonar.sh") if plat in str(p)]
        if not sh:
            sys.exit("SonarQube not found - run ./setup_mac.sh --with-scanners first (or start a SonarQube server on localhost:9000).")
        log("Starting SonarQube in the background (1-3 minutes).")
        subprocess.run(["sh", str(sh[0]), "start"], env=env)
    for _ in range(90):
        time.sleep(5)
        if sonar_up():
            log("SonarQube is UP")
            return
    sys.exit("SonarQube did not start. Check the SonarQube window for errors.")


def sonar_auth():
    """First run: change default admin password + create an analysis token, saved locally."""
    if CRED.exists():
        c = json.loads(CRED.read_text())
        if requests.get(f"{SONAR}/api/authentication/validate", auth=(c["token"], ""), timeout=10).json().get("valid"):
            return c["token"]
    alphabet = string.ascii_letters + string.digits
    pw = "Aa1!" + "".join(secrets.choice(alphabet) for _ in range(16))
    r = requests.post(f"{SONAR}/api/users/change_password",
                      auth=("admin", "admin"),
                      data={"login": "admin", "previousPassword": "admin", "password": pw}, timeout=30)
    if r.status_code not in (200, 204):
        if CRED.exists():
            pw = json.loads(CRED.read_text())["admin_password"]
        else:
            sys.exit(f"Could not set SonarQube password ({r.status_code}): {r.text[:300]}")
    r = requests.post(f"{SONAR}/api/user_tokens/generate", auth=("admin", pw),
                      data={"name": f"study-{int(time.time())}"}, timeout=30)
    r.raise_for_status()
    tok = r.json()["token"]
    CRED.write_text(json.dumps({"admin_password": pw, "token": tok}, indent=2))
    log(f"SonarQube credentials saved locally in {CRED.relative_to(ROOT)} (browser login: admin / see that file)")
    return tok


def sonar_get(tok, path, params):
    r = requests.get(f"{SONAR}{path}", params=params, auth=(tok, ""), timeout=60)
    r.raise_for_status()
    return r.json()


def sonar_scan(tok, key, src_dir, commit_hash, when, workdir):
    if os.name == "nt":
        scanner = next((TOOLS / "scanner").rglob("sonar-scanner.bat"))
    else:
        scanner = next((p for p in (TOOLS / "scanner").rglob("sonar-scanner") if p.parent.name == "bin"), None) \
            or shutil.which("sonar-scanner")
        if not scanner:
            sys.exit("sonar-scanner not found - run ./setup_mac.sh --with-scanners first.")
    shutil.rmtree(workdir, ignore_errors=True)
    workdir.mkdir(parents=True)
    args = [str(scanner),
            f"-Dsonar.host.url={SONAR}", f"-Dsonar.token={tok}",
            f"-Dsonar.projectKey={key}", f"-Dsonar.projectName={key}",
            f"-Dsonar.projectVersion={commit_hash[:10]}",
            f"-Dsonar.projectDate={when}",
            f"-Dsonar.projectBaseDir={src_dir}", "-Dsonar.sources=.",
            "-Dsonar.inclusions=**/*.py", "-Dsonar.python.version=3",
            "-Dsonar.scm.disabled=true", "-Dsonar.qualitygate.wait=false",
            f"-Dsonar.working.directory={workdir}"]
    run(args, cwd=src_dir, timeout=3600)
    task = dict(l.split("=", 1) for l in (workdir / "report-task.txt").read_text().splitlines() if "=" in l)
    tid = task["ceTaskId"]
    for _ in range(360):
        task_info = sonar_get(tok, "/api/ce/task", {"id": tid})["task"]
        st = task_info["status"]
        if st == "SUCCESS":
            break
        if st in ("FAILED", "CANCELED"):
            raise RuntimeError(f"SonarQube background task {st}: {task_info.get('errorMessage', '')[:300]}")
        time.sleep(2)
    issues, page = [], 1
    while True:
        d = sonar_get(tok, "/api/issues/search",
                      {"components": key, "resolved": "false", "ps": 500, "p": page,
                       "additionalFields": "_all"})
        issues += d["issues"]
        if page * 500 >= min(d["paging"]["total"], 10000):
            break
        page += 1
    meas = sonar_get(tok, "/api/measures/component",
                     {"component": key, "metricKeys": "ncloc,files,functions,complexity,cognitive_complexity,"
                      "code_smells,bugs,vulnerabilities,security_hotspots,sqale_index"})
    return issues, meas


# --------------------------------------------------------------- selection
def select_commits(repo_dir, n, mode):
    hashes = git(repo_dir, "rev-list", "--reverse", "--no-merges", "--first-parent", "HEAD").split()
    if mode == "last":
        return hashes[-n:]
    if len(hashes) <= n:
        return hashes
    step = (len(hashes) - 1) / (n - 1)
    return [hashes[round(i * step)] for i in range(n)]


def timeline(repo_dir, out_csv):
    fmt = "%H|%cI|%aI|%an|%P|%s"
    rows = []
    for line in git(repo_dir, "log", "--first-parent", f"--format={fmt}").splitlines():
        h, cdate, adate, author, parents, subj = line.split("|", 5)
        stat = git(repo_dir, "show", "--numstat", "--format=", h, check=False).splitlines()
        py = [s.split("\t") for s in stat if s.count("\t") == 2]
        rows.append({"commit": h, "committer_date": cdate, "author_date": adate, "author": author,
                     "is_merge": len(parents.split()) > 1, "files_changed": len(py),
                     "py_files_changed": sum(p[2].endswith(".py") for p in py),
                     "lines_added": sum(int(p[0]) for p in py if p[0].isdigit()),
                     "lines_deleted": sum(int(p[1]) for p in py if p[1].isdigit()),
                     "subject": subj[:200]})
    rows.reverse()
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    return rows


def py_loc(src_dir):
    total = files = 0
    for p in Path(src_dir).rglob("*.py"):
        if ".git" in p.parts:
            continue
        try:
            total += sum(1 for l in p.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip())
            files += 1
        except OSError:
            pass
    return total, files


# --------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", default=str(ROOT / "data" / "study_repos.csv"))
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--mode", default="last", choices=["last", "spread"])
    ap.add_argument("--skip-sonar", action="store_true")
    ap.add_argument("--out", default=str(RAW), help="output folder for raw results (one per study phase)")
    a = ap.parse_args()

    (ROOT / "data").mkdir(exist_ok=True)
    rules = freeze_semgrep_rules()
    tok = None
    if not a.skip_sonar:
        ensure_sonar()
        tok = sonar_auth()

    with open(a.repos, encoding="utf-8") as f:
        study = list(csv.DictReader(f))
    REPOS.mkdir(exist_ok=True)

    for s in study:
        try:
            scan_one(s, a, rules, tok)
        except Exception as e:                       # one broken repository must not stop the whole scan
            log(f"FAILED {s['repo']}: {str(e)[:300]}")
    log("ALL SCANS FINISHED")


def prepare_clone(full, rdir):
    """Clone without checkout and skip paths that Windows cannot create (e.g. names containing ':').
    Such paths are never .py files, so the analysed code is unchanged."""
    if not (rdir / ".git").exists():
        log(f"Cloning {full}")
        run(["git", *NO_LFS, "clone", "--quiet", "--no-checkout", f"https://github.com/{full}.git", str(rdir)])
    git(rdir, "config", "core.sparseCheckout", "true")
    git(rdir, "config", "core.sparseCheckoutCone", "false")
    info = rdir / ".git" / "info"; info.mkdir(exist_ok=True)
    (info / "sparse-checkout").write_text("/*\n!*:*\n!*\\?*\n!*\\**\n!*\"*\n!*<*\n!*>*\n!*|*\n"
                                        "!**/con\n!**/con.*\n!**/prn\n!**/prn.*\n!**/aux\n!**/aux.*\n!**/nul\n!**/nul.*\n!**/com1\n!**/com1.*\n!**/com2\n!**/com2.*\n!**/com3\n!**/com3.*\n!**/com4\n!**/com4.*\n!**/lpt1\n!**/lpt1.*\n!**/lpt2\n!**/lpt2.*\n!**/lpt3\n!**/lpt3.*\n", encoding="utf-8")


def scan_one(s, a, rules, tok):
        full, group = s["repo"], s["group"]
        name = full.replace("/", "__")
        rdir = REPOS / name
        prepare_clone(full, rdir)
        default = git(rdir, "rev-parse", "--abbrev-ref", "origin/HEAD", check=False).strip().replace("origin/", "") or "HEAD"
        git(rdir, "checkout", "--quiet", "-f", default)
        head = git(rdir, "rev-parse", "HEAD").strip()
        out = Path(a.out) / name
        out.mkdir(parents=True, exist_ok=True)
        tl = {r["commit"]: r for r in timeline(rdir, out / "timeline.csv")}
        commits = select_commits(rdir, a.n, a.mode)
        (out / "selection.json").write_text(json.dumps(
            {"repo": full, "group": group, "head_at_scan": head, "mode": a.mode, "n": a.n,
             "commits": commits}, indent=2))
        log(f"{group} {full}: {len(commits)} commits selected (mode={a.mode})")

        last_when = None
        phase = Path(a.out).name.replace("raw", "").strip("_")
        key = "study_" + (phase + "_" if phase else "") + name.replace(".", "_")
        key += os.environ.get("SONAR_KEY_SUFFIX", "")   # new SonarQube project when a scan is restarted from scratch
        for i, h in enumerate(commits, 1):
            cdir = out / f"{i:03d}_{h[:10]}"
            done_flag = cdir / "DONE"
            when = datetime.fromisoformat(tl[h]["committer_date"]).astimezone(timezone.utc)
            if last_when and when <= last_when:          # SonarQube needs increasing dates
                when = last_when + timedelta(seconds=1)
            last_when = when
            if done_flag.exists():
                continue
            cdir.mkdir(exist_ok=True)
            git(rdir, "checkout", "--quiet", "-f", h)
            git(rdir, "clean", "-fdxq")
            loc, nfiles = py_loc(rdir)
            meta = {"repo": full, "group": group, "index": i, "commit": h,
                    "committer_date": tl[h]["committer_date"], "author": tl[h]["author"],
                    "py_loc_nonblank": loc, "py_files": nfiles, "errors": []}
            t0 = time.time()
            # --- Semgrep
            try:
                cmd = SEMGREP_CMD + ["scan", "--json", "--metrics=off", "--disable-version-check",
                       "--quiet", "--include=*.py", "--timeout=60",
                       f"--output={cdir / 'semgrep.json'}"]
                for r in rules:
                    cmd.append(f"--config={r}")
                cmd.append(str(rdir))
                run(cmd, check=False, timeout=3600)
                if not (cdir / "semgrep.json").exists():
                    meta["errors"].append("semgrep produced no output")
            except Exception as e:
                meta["errors"].append(f"semgrep: {e}")
            # --- SonarQube
            if tok:
                try:
                    issues, meas = sonar_scan(tok, key, rdir, h,
                                              when.strftime("%Y-%m-%dT%H:%M:%S+0000"),
                                              TOOLS / "cache" / "scannerwork" / name)
                    (cdir / "sonar_issues.json").write_text(json.dumps(issues), encoding="utf-8")
                    (cdir / "sonar_measures.json").write_text(json.dumps(meas), encoding="utf-8")
                except Exception as e:
                    meta["errors"].append(f"sonar: {str(e)[:500]}")
            meta["seconds"] = round(time.time() - t0, 1)
            (cdir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
            if not meta["errors"]:
                done_flag.write_text("ok")
            log(f"  {full} [{i}/{len(commits)}] {h[:10]} {tl[h]['committer_date'][:10]} "
                f"LOC={loc} ({meta['seconds']}s){'  ERRORS: ' + '; '.join(meta['errors']) if meta['errors'] else ''}")
        git(rdir, "checkout", "--quiet", "-f", default)


if __name__ == "__main__":
    main()
