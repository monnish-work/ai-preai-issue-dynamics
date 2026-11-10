"""
analyze_v2.py - repository-level analysis (main result) with Holm correction, pooled survival as
supporting evidence (overall and stratified by matched pair), and a reconciliation of issue counts.

Usage:  python scripts/analyze_v2.py <tag>      e.g.  phaseC, phaseC_aligned, phaseC_paired
Options (environment variables, for sensitivity analyses):
  LOC=py_lines_all (default; all lines of .py files = CountLine, as in the professor's replication package)
      or LOC=py_loc (non-blank lines only)
  TIERS=S (only pairs selected with the strict rule: >= 60 commits and >= 2 % declared files)
  MAPPING=sonar (default; SonarQube's own quality classification for every rule)
      or MAPPING=strict (rules marked "Excluded" in mappings/sonar_python_rule_attribute_mapping.csv - rules
      that SonarQube assigns to more than one quality - are dropped, exactly as in the replication package)
Input : data/derived_<tag>/{issue_histories,findings,snapshots}.csv, data/study_repos_phase*.csv (matched pairs)
Output: results_<tag>/v2/{repo_measures,repo_tests,pooled_tests,count_reconciliation,mechanism_shares}.csv

Definitions (used everywhere):
- Analysed commit: one of the sampled non-merge commits of a repository's observation window.
- Groups: "AI-declared" (repositories with an explicit, documented declaration of AI-assisted development)
  and "Pre-AI" (matched repositories whose history ends before AI coding assistants were available).
- Primary findings = the four ISO/IEC 25010 attributes used in the professor's study:
  Maintainability and Reliability (SonarQube), Security (Semgrep), Performance efficiency (Ruff PERF rules).
  "all" = the sum of the four.
- Baseline issue: present at the first analysed commit of the window (introduction unknown, left-censored).
  Excluded from introduction counts, introduction rates and lifetimes; included in removal counts
  labelled "removed (all)" and in densities.
- Introduced issue: first seen at analysed commit k >= 2 of the window.
- Removed: absent at a later analysed commit (first absence = removal commit).
- Right-censored: still present at the last analysed commit.
- Lifetime (commits): number of analysed commits from introduction to removal, or to the last
  analysed commit if censored. Lifetime (days): calendar days for the same interval.
- Density: open primary findings per KLOC (1,000 lines of Python, generated and vendored folders excluded;
  all lines by default, see LOC) at the last analysed commit, and averaged over all analysed commits.
"""
import os, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
TAG = sys.argv[1] if len(sys.argv) > 1 else "phaseC"
D = ROOT / "data" / f"derived_{TAG}"
SUB = os.environ.get("SUBDIR", "v2")
R = ROOT / f"results_{TAG}" / SUB
R.mkdir(parents=True, exist_ok=True)
PRIMARY = {("sonarqube", "maintainability"), ("sonarqube", "reliability"), ("semgrep", "security"), ("ruff", "performance")}
CATS = ["all", "maintainability", "reliability", "security", "performance"]
LOC = os.environ.get("LOC", "py_lines_all")
MAPPING = os.environ.get("MAPPING", "sonar")
SUB = os.environ.get("SUBDIR", "v2")

H = pd.read_csv(D / "issue_histories.csv", keep_default_na=False)
S = pd.read_csv(D / "snapshots.csv", keep_default_na=False)
F = pd.read_csv(D / "findings.csv", keep_default_na=False, usecols=["repo", "snapshot", "issue_id", "tool", "rule", "category"])
S["kloc_src"] = S[LOC].astype(float)
GL = {"AI": "AI-declared", "PreAI": "Pre-AI"}          # group labels used in every output
H["group"] = H.group.replace(GL); S["group"] = S.group.replace(GL)
if MAPPING == "strict":
    _m = pd.read_csv(ROOT / "mappings" / "sonar_python_rule_attribute_mapping.csv")
    _ex = set(_m[_m.mapped_quality_attribute == "Excluded"].rule_id)
    H = H[~H.rule.isin(_ex)]; F = F[~F.rule.isin(_ex)]
_st = pd.concat([pd.read_csv(f) for f in sorted((ROOT / "data").glob("study_repos_phase*.csv"))])
if "tier" not in _st.columns:
    _st["tier"] = "S"
_st["tier"] = _st.tier.fillna("S")
pairs = _st.set_index("repo").match_id.to_dict()
TIERS = os.environ.get("TIERS", "")          # e.g. TIERS=S : only pairs selected with the strict rule (sensitivity)
if TIERS:
    keep = set(_st[_st.tier.isin(TIERS.split(","))].repo)
    H = H[H.repo.isin(keep)]; S = S[S.repo.isin(keep)]; F = F[F.repo.isin(keep)]

H["primary"] = [(t, c) in PRIMARY for t, c in zip(H.tool, H.category)]
H["baseline"] = H.present_at_first_snapshot.astype(str) == "True"
H["removed"] = H.removed_commit != ""
H["lifetime_snapshots"] = H.lifetime_snapshots.astype(float)
H["lifetime_days"] = H.lifetime_days.astype(float)
P = H[H.primary].copy()
F = F[[(t, c) in PRIMARY for t, c in zip(F.tool, F.category)]]


def km(t, e):
    d = pd.DataFrame({"t": t, "e": e.astype(int)}).sort_values("t")
    s, n, pts = 1.0, len(d), [(0.0, 1.0)]
    for tt, g in d.groupby("t"):
        ev = g.e.sum()
        if ev:
            s *= 1 - ev / n
            pts.append((tt, s))
        n -= len(g)
    return pts


def km_median(t, e):
    if len(t) == 0:
        return np.nan
    for tt, s in km(t, e):
        if s <= 0.5:
            return tt
    return np.nan


def logrank_parts(t1, e1, t2, e2):
    t = np.concatenate([t1, t2]); e = np.concatenate([e1, e2]).astype(int)
    g = np.concatenate([np.zeros(len(t1)), np.ones(len(t2))])
    O = E = V = 0.0
    for ut in np.unique(t[e == 1]):
        r = t >= ut; n = r.sum(); n1 = (r & (g == 0)).sum()
        d = ((t == ut) & (e == 1)).sum(); d1 = ((t == ut) & (e == 1) & (g == 0)).sum()
        O += d1; E += d * n1 / n
        if n > 1:
            V += d * (n1 / n) * (1 - n1 / n) * (n - d) / (n - 1)
    return O, E, V


def chi_p(O, E, V):
    if V <= 0:
        return np.nan, np.nan
    c = (O - E) ** 2 / V
    return c, 1 - stats.chi2.cdf(c, 1)


def cliffs(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if not len(a) or not len(b):
        return np.nan
    return (sum((x > b).sum() for x in a) - sum((x < b).sum() for x in a)) / (len(a) * len(b))


def holm(p):
    p = np.asarray(p, float); m = np.isfinite(p).sum(); out = np.full(len(p), np.nan)
    order = [i for i in np.argsort(p) if np.isfinite(p[i])]
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p[i]))
        out[i] = running
    return out


# ------------------------------------------------------------------ repository measures
rows = []
for repo, s in S.groupby("repo"):
    s = s.sort_values("index")
    kloc_mean = s.kloc_src.mean() / 1000
    last = s.iloc[-1]; kloc_last = float(last.kloc_src) / 1000
    ok = s[~s.missing_tools.str.contains("sonarqube")]
    f = F[F.repo == repo]
    row = {"repo": repo, "group": s.group.iloc[0], "pair": pairs.get(repo, ""), "analysed_commits": len(s),
           "window_start": s.date.iloc[0][:10], "window_end": s.date.iloc[-1][:10],
           "mean_kloc": round(kloc_mean, 2), "last_kloc": round(kloc_last, 2)}
    for c in CATS:
        h = P[(P.repo == repo) & ((P.category == c) if c != "all" else True)]
        w = h[~h.baseline]
        fc = f if c == "all" else f[f.category == c]
        per_snap = fc.groupby("snapshot").size()
        dens = [per_snap.get(int(i), 0) / (float(l) / 1000) for i, l in zip(ok["index"], ok.kloc_src) if float(l) > 0]
        last_ok = ok.iloc[-1] if len(ok) else last
        row.update({
            f"{c}_baseline": int(h.baseline.sum()), f"{c}_introduced": len(w),
            f"{c}_removed_all": int(h.removed.sum()), f"{c}_removed_in_window": int(w.removed.sum()),
            f"{c}_intro_per_kloc": round(len(w) / kloc_mean, 3) if kloc_mean else np.nan,
            f"{c}_removed_per_kloc": round(h.removed.sum() / kloc_mean, 3) if kloc_mean else np.nan,
            f"{c}_intro_per_kloc_per_commit": round(len(w) / kloc_mean / max(1, len(s) - 1), 4) if kloc_mean else np.nan,
            f"{c}_removed_per_kloc_per_commit": round(h.removed.sum() / kloc_mean / max(1, len(s) - 1), 4) if kloc_mean else np.nan,
            f"{c}_density_last": round(per_snap.get(int(last_ok["index"]), 0) / (float(last_ok.kloc_src) / 1000), 3) if float(last_ok.kloc_src) else np.nan,
            f"{c}_density_mean": round(float(np.mean(dens)), 3) if dens else np.nan,
            f"{c}_removed_share": round(w.removed.mean(), 3) if len(w) else np.nan,
            f"{c}_median_life_commits": km_median(w.lifetime_snapshots.values, w.removed.values),
        })
    rem = P[(P.repo == repo) & P.removed]
    for m in ("code_changed", "file_deleted", "code_still_present"):
        row[f"share_{m}"] = round((rem.removal_mechanism == m).mean(), 3) if len(rem) else np.nan
    rows.append(row)
RM = pd.DataFrame(rows)
RM.to_csv(R / "repo_measures.csv", index=False)

# ------------------------------------------------------------------ repository-level tests (main result)
measures = ["intro_per_kloc", "removed_per_kloc", "intro_per_kloc_per_commit", "removed_per_kloc_per_commit", "density_last", "density_mean", "removed_share", "median_life_commits"]
tests = []
for c in CATS:
    for m in measures:
        col = f"{c}_{m}"
        a = RM[RM.group == "AI-declared"][col].dropna().values; b = RM[RM.group == "Pre-AI"][col].dropna().values
        if len(a) >= 2 and len(b) >= 2 and np.ptp(np.concatenate([a, b])) > 0:
            u = stats.mannwhitneyu(a, b, alternative="two-sided", method="exact")
            U, p = u.statistic, u.pvalue
        else:
            U, p = np.nan, np.nan
        tests.append({"category": c, "measure": m, "n_AI_declared": len(a), "n_PreAI": len(b),
                      "AI_declared_median": np.median(a) if len(a) else np.nan, "PreAI_median": np.median(b) if len(b) else np.nan,
                      "U": U, "p": p, "cliffs_delta": cliffs(a, b)})
T = pd.DataFrame(tests)
T["p_holm"] = holm(T.p.values)          # one family: every repository-level test in this table
T = T.round(4)
T.to_csv(R / "repo_tests.csv", index=False)

# ------------------------------------------------------------------ pooled survival (supporting evidence)
pt = []
for unit, col in (("commits", "lifetime_snapshots"), ("days", "lifetime_days")):
    for c in CATS:
        w = P[~P.baseline & ((P.category == c) if c != "all" else True)]
        a, b = w[w.group == "AI-declared"], w[w.group == "Pre-AI"]
        if not len(a) or not len(b):
            continue
        chi, p = chi_p(*logrank_parts(a[col].values, a.removed.values, b[col].values, b.removed.values))
        O = E = V = 0.0                     # stratified by matched pair: compares AI vs Pre-AI inside each pair
        for pr in sorted(set(pairs.values())):
            reps = [r for r, x in pairs.items() if x == pr]
            ww = w[w.repo.isin(reps)]
            aa, bb = ww[ww.group == "AI-declared"], ww[ww.group == "Pre-AI"]
            if len(aa) and len(bb):
                o, e, v = logrank_parts(aa[col].values, aa.removed.values, bb[col].values, bb.removed.values)
                O += o; E += e; V += v
        chi_s, p_s = chi_p(O, E, V)
        pt.append({"unit": unit, "category": c, "n_AI_declared": len(a), "n_PreAI": len(b),
                   "AI_declared_km_median": km_median(a[col].values, a.removed.values),
                   "PreAI_km_median": km_median(b[col].values, b.removed.values),
                   "logrank_chi2": chi, "logrank_p": p, "pair_stratified_chi2": chi_s, "pair_stratified_p": p_s})
pd.DataFrame(pt).round(4).to_csv(R / "pooled_tests.csv", index=False)

# ------------------------------------------------------------------ reconciliation of counts
allh, prim = H, P
rec = [
    {"set": "A. All issue histories (every tool-category pair)", "histories": len(allh), "removed": int(allh.removed.sum()), "file": "issue_histories.csv"},
    {"set": "B. Primary categories only (SonarQube M+R, Semgrep S, Ruff P)", "histories": len(prim), "removed": int(prim.removed.sum()), "file": "rates (removed_all), mechanism shares"},
    {"set": "   of which baseline issues (present at first analysed commit)", "histories": int(prim.baseline.sum()), "removed": int((prim.removed & prim.baseline).sum()), "file": ""},
    {"set": "C. Primary, introduced in window (baseline excluded)", "histories": int((~prim.baseline).sum()), "removed": int((prim.removed & ~prim.baseline).sum()), "file": "lifetimes, survival curves, removed_in_window"},
    {"set": "   of which right-censored (open at last analysed commit)", "histories": int((~prim.baseline & ~prim.removed).sum()), "removed": 0, "file": ""},
]
pd.DataFrame(rec).to_csv(R / "count_reconciliation.csv", index=False)

mech = (P[P.removed].groupby(["group", "removal_mechanism"]).size().unstack(fill_value=0))
mech_share = mech.div(mech.sum(axis=1), axis=0).round(3)
pd.concat({"count": mech, "share": mech_share}, axis=1).to_csv(R / "mechanism_shares.csv")

pd.set_option("display.width", 250)
print(f"== {TAG}")
print(pd.DataFrame(rec).to_string(index=False))
print(T[T.category == "all"].to_string(index=False))
print(pd.DataFrame(pt)[lambda d: d.unit == "commits"].round(4).to_string(index=False))
print(mech_share)
