"""
process_metrics.py - development-process metrics per repository and observation window, compared AI-declared
vs Pre-AI at repository level (Mann-Whitney U exact, Cliff's delta, Holm correction within this family).

Metrics follow the developer-activity measures of the professor's study (Table 4 of the replication package:
commits per author, distinct authors, developer experience). Exact definitions used here:
- Window commits: non-merge commits reachable from the last analysed commit and not from the parent(s) of the
  first analysed commit, i.e. every non-merge commit of the observation window, not only the sampled ones.
- commits: number of window commits.            commits_per_month: commits / window length in months (30.44 d).
- distinct_authors: distinct authors of window commits (identity = lower-cased e-mail; bot accounts such as
  dependabot / github-actions / pre-commit-ci are excluded).
- commits_per_author: commits / distinct_authors.
- dev_experience_days: for each window commit, days between that commit and its author's first commit in the
  whole repository history; averaged over the window commits (experience of the person making the change).
- dev_experience_author_days: the same, but averaged over authors (each author counted once, at their last
  window commit).

Usage:  python scripts/process_metrics.py <tag>      (tag = phaseC, phaseC_aligned, phaseC_paired)
Output: results_<tag>/v2/process_metrics.csv, results_<tag>/v2/process_tests.csv
"""
import subprocess, sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
TAG = sys.argv[1] if len(sys.argv) > 1 else "phaseC"
S = pd.read_csv(ROOT / "data" / f"derived_{TAG}" / "snapshots.csv", keep_default_na=False)
R = ROOT / f"results_{TAG}" / "v2"; R.mkdir(parents=True, exist_ok=True)
BOT = ("[bot]", "dependabot", "github-actions", "pre-commit-ci", "noreply@github.com>")


def git(repo, *a):
    return subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def log(repo, *rev):
    out = []
    for l in git(repo, "log", "--no-merges", "--format=%H\t%ae\t%an\t%aI", *rev).splitlines():
        h, e, n, d = l.split("\t")
        out.append((h, e.lower().strip(), n, datetime.fromisoformat(d)))
    return out


def is_bot(e, n):
    s = (e + " " + n).lower()
    return any(b in s for b in ("[bot]", "dependabot", "github-actions", "pre-commit-ci"))


rows = []
for repo_name, s in S.groupby("repo"):
    s = s.sort_values("index")
    repo = ROOT / "repos" / repo_name.replace("/", "__")
    first, last = s.commit.iloc[0], s.commit.iloc[-1]
    parents = git(repo, "rev-list", "--parents", "-n", "1", first).split()[1:]
    win = log(repo, last, *[f"^{p}" for p in parents])
    win = [c for c in win if not is_bot(c[1], c[2])]
    hist = [c for c in log(repo, last) if not is_bot(c[1], c[2])]
    first_seen = {}
    for h, e, n, d in sorted(hist, key=lambda c: c[3]):
        first_seen.setdefault(e, d)
    authors = sorted({c[1] for c in win})
    t0, t1 = min(c[3] for c in win), max(c[3] for c in win)
    months = max((t1 - t0).days / 30.44, 1.0)
    exp_c = [(d - first_seen[e]).total_seconds() / 86400 for h, e, n, d in win]
    last_by_author = {}
    for h, e, n, d in win:
        last_by_author[e] = max(d, last_by_author.get(e, d))
    exp_a = [(d - first_seen[e]).total_seconds() / 86400 for e, d in last_by_author.items()]
    rows.append({"repo": repo_name, "group": {"AI": "AI-declared", "PreAI": "Pre-AI"}[s.group.iloc[0]], "window_start": t0.date(), "window_end": t1.date(),
                 "commits": len(win), "commits_per_month": round(len(win) / months, 2),
                 "distinct_authors": len(authors), "commits_per_author": round(len(win) / len(authors), 2),
                 "dev_experience_days": round(float(np.mean(exp_c)), 1),
                 "dev_experience_author_days": round(float(np.mean(exp_a)), 1)})
PM = pd.DataFrame(rows)
PM.to_csv(R / "process_metrics.csv", index=False)


def cliffs(a, b):
    return (sum((x > b).sum() for x in a) - sum((x < b).sum() for x in a)) / (len(a) * len(b))


def holm(p):
    p = np.asarray(p, float); out = np.full(len(p), np.nan); run = 0.0
    order = [i for i in np.argsort(p) if np.isfinite(p[i])]; m = len(order)
    for k, i in enumerate(order):
        run = max(run, min(1.0, (m - k) * p[i])); out[i] = run
    return out


T = []
for m in ["commits", "commits_per_month", "distinct_authors", "commits_per_author", "dev_experience_days", "dev_experience_author_days"]:
    a = PM[PM.group == "AI-declared"][m].astype(float).values; b = PM[PM.group == "Pre-AI"][m].astype(float).values
    p = stats.mannwhitneyu(a, b, alternative="two-sided", method="exact").pvalue if np.ptp(np.r_[a, b]) > 0 else np.nan
    T.append({"measure": m, "AI_declared_median": np.median(a), "PreAI_median": np.median(b), "p": p, "cliffs_delta": cliffs(a, b)})
T = pd.DataFrame(T); T["p_holm"] = holm(T.p.values)
T.round(4).to_csv(R / "process_tests.csv", index=False)
print(PM.to_string(index=False)); print(T.round(4).to_string(index=False))
