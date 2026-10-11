"""
analyze.py  -  Phase D/E: measures, AI vs PreAI comparison, Kaplan-Meier curves.

Input : data/derived/issue_histories.csv, data/derived/snapshots.csv
Output: results/rates_by_repo.csv, results/lifetime_summary.csv, results/logrank_tests.csv,
        results/removal_mechanisms.csv, results/figures/*.png

Operationalization (primary):  maintainability & reliability = SonarQube findings,
security = Semgrep findings (brief section 4). Secondary tables use every tool/category pair.
Issues already present at the first analysed snapshot are LEFT-censored (introduction time
unknown): counted as 'baseline', excluded from introduction rates and survival curves.
Issues still present at the last snapshot are RIGHT-censored.
"""
import math
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
PHASE = sys.argv[1] if len(sys.argv) > 1 else ""   # e.g. "phaseC"; empty = pilot
SFX = ("_" + PHASE) if PHASE else ""
D = ROOT / "data" / ("derived" + SFX)
R = ROOT / ("results" + SFX); FIG = R / "figures"
FIG.mkdir(parents=True, exist_ok=True)

COL = {"AI": "#2a78d6", "PreAI": "#eb6834"}          # categorical slots 1-2 (validated palette)
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e0"
PRIMARY = {("sonarqube", "maintainability"), ("sonarqube", "reliability"), ("semgrep", "security")}
CATS = ["maintainability", "reliability", "security"]

plt.rcParams.update({"font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.8, "figure.dpi": 150, "savefig.bbox": "tight"})


# ------------------------------------------------------------------ helpers
def km(durations, observed):
    """Kaplan-Meier estimate. Returns (times, survival, n_at_risk_at_times)."""
    d = pd.DataFrame({"t": durations, "e": observed.astype(int)}).sort_values("t")
    times, surv, s = [0.0], [1.0], 1.0
    n = len(d)
    for t, g in d.groupby("t"):
        events = g["e"].sum()
        if events:
            s *= 1 - events / n
            times.append(t); surv.append(s)
        n -= len(g)
    return np.array(times), np.array(surv)


def km_median(t, s):
    below = np.where(s <= 0.5)[0]
    return float(t[below[0]]) if len(below) else float("nan")


def logrank(t1, e1, t2, e2):
    """Two-group log-rank test (chi-square, 1 df)."""
    t = np.concatenate([t1, t2]); e = np.concatenate([e1, e2]).astype(int)
    g = np.concatenate([np.zeros(len(t1)), np.ones(len(t2))])
    O1 = E1 = V = 0.0
    for ut in np.unique(t[e == 1]):
        at_risk = t >= ut
        n, n1 = at_risk.sum(), (at_risk & (g == 0)).sum()
        d = ((t == ut) & (e == 1)).sum(); d1 = ((t == ut) & (e == 1) & (g == 0)).sum()
        O1 += d1; E1 += d * n1 / n
        if n > 1:
            V += d * (n1 / n) * (1 - n1 / n) * (n - d) / (n - 1)
    if V == 0:
        return float("nan"), float("nan")
    chi = (O1 - E1) ** 2 / V
    return chi, 1 - stats.chi2.cdf(chi, 1)


def cliffs_delta(a, b):
    a, b = np.asarray(a), np.asarray(b)
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    gt = sum((x > b).sum() for x in a); lt = sum((x < b).sum() for x in a)
    return (gt - lt) / (len(a) * len(b))


# ------------------------------------------------------------------ load
H = pd.read_csv(D / "issue_histories.csv")
S = pd.read_csv(D / "snapshots.csv")
H["primary"] = [(t, c) in PRIMARY for t, c in zip(H.tool, H.category)]
H["removed"] = ~H["censored"].astype(bool)
H["baseline"] = H["present_at_first_snapshot"].astype(bool)
P = H[H.primary].copy()

# ------------------------------------------------------------------ RQ1 + remediation rates
rows = []
for repo, s in S.groupby("repo"):
    s = s.sort_values("index")
    grp = s.group.iloc[0]
    kloc = s.py_loc.mean() / 1000
    n_int = len(s) - 1
    days = (pd.to_datetime(s.date.iloc[-1], utc=True) - pd.to_datetime(s.date.iloc[0], utc=True)).days
    for cat in CATS + ["all"]:
        h = P[(P.repo == repo) & ((P.category == cat) if cat != "all" else True)]
        intro = int((~h.baseline).sum())
        removed = int(h.removed.sum())
        base = int(h.baseline.sum())
        rows.append({"repo": repo, "group": grp, "category": cat, "snapshots": len(s),
                     "commit_intervals": n_int, "days_observed": days, "mean_kloc": round(kloc, 2),
                     "baseline_issues": base, "introduced": intro, "removed": removed,
                     "open_at_end": int(h.censored.astype(bool).sum()),
                     "intro_per_kloc": round(intro / kloc, 3) if kloc else None,
                     "intro_per_commit": round(intro / n_int, 3) if n_int else None,
                     "removed_per_kloc": round(removed / kloc, 3) if kloc else None,
                     "removed_per_commit": round(removed / n_int, 3) if n_int else None,
                     "remediation_share": round(removed / (base + intro), 3) if base + intro else None,
                     "density_start_per_kloc": round(base / (s.py_loc.iloc[0] / 1000), 3),
                     })
rates = pd.DataFrame(rows)
rates.to_csv(R / "rates_by_repo.csv", index=False)

# ------------------------------------------------------------------ RQ2 / RQ3 survival
life_rows, lr_rows = [], []
W = P[~P.baseline]            # issues introduced inside the observation window
for unit, col in (("days", "lifetime_days"), ("snapshots", "lifetime_snapshots")):
    for cat in CATS + ["all"]:
        w = W if cat == "all" else W[W.category == cat]
        grp_data = {}
        for g in ("AI", "PreAI"):
            x = w[w.group == g]
            t, e = x[col].to_numpy(float), x.removed.to_numpy()
            grp_data[g] = (t, e)
            if len(x):
                kt, ks = km(t, e)
                life_rows.append({"unit": unit, "category": cat, "group": g, "n_issues": len(x),
                                  "n_removed": int(e.sum()), "n_censored": int((~e).sum()),
                                  "km_median": km_median(kt, ks),
                                  "mean_lifetime_removed_only": round(t[e].mean(), 3) if e.any() else None})
        if all(len(v[0]) for v in grp_data.values()):
            chi, p = logrank(*grp_data["AI"], *grp_data["PreAI"])
            a, b = grp_data["AI"], grp_data["PreAI"]
            lr_rows.append({"unit": unit, "category": cat, "n_AI": len(a[0]), "n_PreAI": len(b[0]),
                            "logrank_chi2": round(chi, 3), "p_value": round(p, 4),
                            "cliffs_delta_removed_only(AI vs PreAI)": round(cliffs_delta(a[0][a[1]], b[0][b[1]]), 3)})
pd.DataFrame(life_rows).to_csv(R / "lifetime_summary.csv", index=False)
pd.DataFrame(lr_rows).to_csv(R / "logrank_tests.csv", index=False)

# RQ3: security vs maintainability/reliability within each group
rq3 = []
for g in ("AI", "PreAI"):
    for unit, col in (("days", "lifetime_days"), ("snapshots", "lifetime_snapshots")):
        x = W[W.group == g]
        sec, oth = x[x.category == "security"], x[x.category != "security"]
        if len(sec) and len(oth):
            chi, p = logrank(sec[col].to_numpy(float), sec.removed.to_numpy(),
                             oth[col].to_numpy(float), oth.removed.to_numpy())
            rq3.append({"group": g, "unit": unit, "n_security": len(sec), "n_other": len(oth),
                        "security_removed_share": round(sec.removed.mean(), 3),
                        "other_removed_share": round(oth.removed.mean(), 3),
                        "logrank_chi2": round(chi, 3), "p_value": round(p, 4)})
pd.DataFrame(rq3).to_csv(R / "rq3_security_vs_other.csv", index=False)

# removal mechanisms (brief rule: disappearance != intentional fix)
mech = (P[P.removed].groupby(["group", "category", "removal_mechanism"]).size()
        .rename("n").reset_index())
mech.to_csv(R / "removal_mechanisms.csv", index=False)


# ------------------------------------------------------------------ figures
def km_plot(unit, col, fname, xlabel):
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
    for ax, cat in zip(axes, CATS):
        w = W[W.category == cat]
        for g in ("AI", "PreAI"):
            x = w[w.group == g]
            if len(x) == 0:
                continue
            t, s = km(x[col].to_numpy(float), x.removed.to_numpy())
            tmax = max(t[-1], x[col].max())
            ax.step(np.append(t, tmax), np.append(s, s[-1]), where="post", color=COL[g], lw=2)
        n_ai, n_pre = (w.group == "AI").sum(), (w.group == "PreAI").sum()
        ev = int(w.removed.sum())
        ax.text(0.98, 0.98, f"AI n={n_ai} | PreAI n={n_pre}\nremovals observed: {ev}", transform=ax.transAxes,
                ha="right", va="top", fontsize=8.5, color=INK2)
        ax.set_title(cat.capitalize(), color=INK, fontsize=11, loc="left")
        ax.set_xlim(left=0)
        ax.set_xlabel(xlabel); ax.set_ylim(0, 1.03)
    axes[0].set_ylabel("Share of issues still present")
    handles = [plt.Line2D([], [], color=COL[g], lw=2) for g in COL]
    fig.legend(handles, list(COL), loc="upper right", frameon=False, ncol=2, bbox_to_anchor=(1, 1.02))
    fig.suptitle(f"Issue survival (Kaplan-Meier), AI vs PreAI, by {unit}", x=0.01, y=1.04, ha="left",
                 color=INK, fontsize=12)
    fig.savefig(FIG / fname); plt.close(fig)


if len(W):
    km_plot("days", "lifetime_days", "km_days.png", "Days since introduction")
    km_plot("commits", "lifetime_snapshots", "km_commits.png", "Analysed commits since introduction")

r = rates[rates.category != "all"]
fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
for ax, (m, lab) in zip(axes, (("intro_per_kloc", "Introduced per KLOC"),
                               ("removed_per_kloc", "Removed per KLOC"))):
    x = np.arange(len(CATS)); wbar = 0.38
    for j, g in enumerate(("AI", "PreAI")):
        vals = [r[(r.group == g) & (r.category == c)][m].mean() for c in CATS]
        ax.set_axisbelow(True)
        bars = ax.bar(x + (j - 0.5) * (wbar + 0.02), vals, wbar, color=COL[g], label=g)
        for b, v in zip(bars, vals):
            if not math.isnan(v):
                ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.2f}", ha="center", va="bottom",
                        fontsize=8, color=INK2)
    ax.set_xticks(x, [c.capitalize() for c in CATS]); ax.set_title(lab, loc="left", color=INK)
    ax.grid(axis="x", visible=False)
axes[1].legend(frameon=False)
fig.suptitle("Issue introduction and removal rates (per 1,000 lines of Python)", x=0.01, y=1.04, ha="left",
             color=INK, fontsize=12)
fig.savefig(FIG / "rates_per_kloc.png"); plt.close(fig)

# open issues over time (stock) per repo
fig, ax = plt.subplots(figsize=(8, 3.6))
F = pd.read_csv(D / "findings.csv")
F = F[[(t, c) in PRIMARY for t, c in zip(F.tool, F.category)]]
for repo, f in F.groupby("repo"):
    g = f.group.iloc[0]
    s = S[S.repo == repo].set_index("index")
    ok = s[~s.missing_tools.fillna("").str.contains("sonarqube")].index
    dens = (f.groupby("snapshot").size() / (s.py_loc / 1000)).reindex(ok)
    ax.plot(dens.index, dens.values, color=COL[g], lw=2, marker="o", ms=3)
    ax.annotate(repo.split("/")[1], xy=(dens.index[-1], dens.values[-1]), xytext=(4, 0),
                textcoords="offset points", color=INK2, fontsize=9, va="center")
ax.set_xlabel("Analysed commit (1 = first in window)"); ax.set_ylabel("Open findings per KLOC")
ax.set_title("Open findings per KLOC across the 30 analysed commits (failed scans skipped)", loc="left", color=INK)
fig.savefig(FIG / "density_over_time.png"); plt.close(fig)

print("Results written to", R)
print(rates[rates.category == "all"][["repo", "group", "baseline_issues", "introduced", "removed",
                                       "intro_per_kloc", "removed_per_kloc"]].to_string(index=False))

# ------------------------------------------------------------------ repo-level comparison
# Issues inside one repository are not independent, so the repository is the unit of
# analysis for the headline AI-vs-PreAI test (Mann-Whitney U, exact, two-sided).
rl = []
for repo, s in S.groupby("repo"):
    w = W[W.repo == repo]
    row = {"repo": repo, "group": s.group.iloc[0]}
    for unit, col in (("snapshots", "lifetime_snapshots"), ("days", "lifetime_days")):
        if len(w):
            t, sv = km(w[col].to_numpy(float), w.removed.to_numpy())
            row[f"km_median_{unit}"] = km_median(t, sv)
        row[f"removed_share"] = round(w.removed.mean(), 3) if len(w) else None
        row["file_deleted_share_of_removals"] = round((w[w.removed].removal_mechanism == "file_deleted").mean(), 3) if w.removed.any() else None
    ra = rates[(rates.repo == repo) & (rates.category == "all")].iloc[0]
    row.update({"intro_per_kloc": ra.intro_per_kloc, "removed_per_kloc": ra.removed_per_kloc,
                "intro_per_commit": ra.intro_per_commit, "mean_kloc": ra.mean_kloc})
    rl.append(row)
RL = pd.DataFrame(rl)
RL.to_csv(R / "repo_level_measures.csv", index=False)
tests = []
for m in ["intro_per_kloc", "removed_per_kloc", "intro_per_commit", "removed_share",
          "km_median_snapshots", "km_median_days", "file_deleted_share_of_removals"]:
    a = RL[RL.group == "AI"][m].dropna().to_numpy(float); b = RL[RL.group == "PreAI"][m].dropna().to_numpy(float)
    if len(a) >= 2 and len(b) >= 2:
        u = stats.mannwhitneyu(a, b, alternative="two-sided", method="exact")
        tests.append({"measure": m, "AI_median": round(float(np.median(a)), 3), "PreAI_median": round(float(np.median(b)), 3),
                      "n_AI": len(a), "n_PreAI": len(b), "U": u.statistic, "p_value": round(u.pvalue, 4),
                      "cliffs_delta": round(cliffs_delta(a, b), 3)})
pd.DataFrame(tests).to_csv(R / "repo_level_tests.csv", index=False)
print(pd.DataFrame(tests).to_string(index=False))
