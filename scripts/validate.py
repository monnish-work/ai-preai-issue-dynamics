"""
validate.py  -  Phase B validation of the issue tracker.

(1) Agreement with SonarQube's own internal issue tracking (independent reference):
    - split   : one SonarQube issue key spread over >1 of our issue histories
                (our tracker lost the issue and re-created it)
    - merged  : one of our histories containing >1 SonarQube key
                (our tracker joined two different issues)
(2) A stratified sample of 10 issue histories for MANUAL checking, with GitHub links
    to the code at introduction, last sighting and removal.

Output: results/validation_sonar_agreement.csv, results/manual_validation_sample.csv,
        results/manual_validation_sample.md
"""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PHASE = sys.argv[1] if len(sys.argv) > 1 else ""   # e.g. "phaseC"; empty = pilot
SFX = ("_" + PHASE) if PHASE else ""
D, R = ROOT / "data" / ("derived" + SFX), ROOT / ("results" + SFX)
R.mkdir(exist_ok=True)
H = pd.read_csv(D / "issue_histories.csv", keep_default_na=False)
F = pd.read_csv(D / "findings.csv", keep_default_na=False)
M = pd.read_csv(D / "match_log.csv", keep_default_na=False)

# ---------------- (1) agreement with SonarQube tracking
sq = H[H.tool == "sonarqube"].copy()
sq["n_keys"] = sq.sonar_keys.str.split("|").apply(len)
key_to_ours = F[F.tool == "sonarqube"].groupby("sonar_key").issue_id.nunique()
rows = []
for repo, g in sq.groupby("repo"):
    keys = F[(F.tool == "sonarqube") & (F.repo == repo)].groupby("sonar_key").issue_id.nunique()
    rows.append({"repo": repo, "our_histories": len(g), "sonar_keys": len(keys),
                 "merged_histories(>1 key)": int((g.n_keys > 1).sum()),
                 "split_keys(>1 history)": int((keys > 1).sum()),
                 "agreement_pct": round(100 * (1 - ((g.n_keys > 1).sum() + (keys > 1).sum()) /
                                               max(1, len(keys))), 2)})
ag = pd.DataFrame(rows)
mm = M.groupby(["repo", "tool", "method"]).agg(n=("cur", "size"), ambiguous=("ambiguous", lambda x: (x.astype(str) == "True").sum())).reset_index()
ag.to_csv(R / "validation_sonar_agreement.csv", index=False)
mm.to_csv(R / "validation_match_methods.csv", index=False)
print(ag.to_string(index=False)); print(mm.to_string(index=False))

# ---------------- (2) stratified manual sample (fixed seed -> reproducible)
W = H[H.present_at_first_snapshot.astype(str) == "False"]
picks = []
def take(df, n):
    df = df[~df.issue_id.isin([p.issue_id for p in picks])]
    for _, r in df.sample(min(n, len(df)), random_state=42).iterrows():
        picks.append(r)
for g in ("AI", "PreAI"):
    w = W[W.group == g]
    take(w[(w.removed_commit != "") & (w.removal_mechanism == "code_changed")], 2)
    take(w[(w.removed_commit != "") & (w.removal_mechanism != "code_changed")], 1)
    take(w[w.moved.astype(str) == "True"], 1)
    take(w[w.removed_commit == ""], 1)
for g in ("AI", "PreAI", "AI", "PreAI", "AI", "PreAI"):     # top up to 10 if a stratum was empty
    if len(picks) >= 10:
        break
    take(W[W.group == g], 1)
S = pd.DataFrame(picks)

def link(repo, commit, path, line=None):
    if not commit:
        return ""
    return f"https://github.com/{repo}/blob/{commit}/{path}" + (f"#L{line}" if line else "")

out = []
for _, r in S.iterrows():
    hist = F[F.issue_id == r.issue_id].sort_values("snapshot")
    last = hist.iloc[-1]
    out.append({
        "issue_id": r.issue_id, "group": r.group, "repo": r.repo, "tool": r.tool, "rule": r.rule,
        "category": r.category, "message": r.message[:120],
        "introduced_commit": r.introduced_commit[:10], "introduced_date": r.introduced_date[:10],
        "seen_in_snapshots": f"{r.introduced_snapshot}-{r.last_seen_snapshot}",
        "lines_seen": " > ".join(dict.fromkeys(str(x) for x in hist.line)),
        "paths_seen": " > ".join(dict.fromkeys(hist.path)),
        "removed_commit": r.removed_commit[:10], "removal_mechanism": r.removal_mechanism or "still open (censored)",
        "link_introduced": link(r.repo, r.introduced_commit, r.path_first, r.line_first),
        "link_last_seen": link(r.repo, last.commit, last.path, last.line),
        "link_removal_diff": f"https://github.com/{r.repo}/commit/{r.removed_commit}" if r.removed_commit else "",
        "CHECK_intro_correct(Y/N)": "", "CHECK_persistence_correct(Y/N)": "",
        "CHECK_removal_correct(Y/N)": "", "notes": ""})
V = pd.DataFrame(out)
V.to_csv(R / "manual_validation_sample.csv", index=False)
with open(R / "manual_validation_sample.md", "w", encoding="utf-8") as f:
    f.write("# Manual validation sample (10 issue histories, seed 42)\n\n")
    for _, v in V.iterrows():
        f.write(f"## Issue {v.issue_id} - {v.group} - {v.repo}\n- Tool/rule: {v.tool} `{v.rule}` ({v.category})\n"
                f"- Message: {v.message}\n- Introduced: {v.introduced_commit} ({v.introduced_date}); "
                f"seen in snapshots {v.seen_in_snapshots}; lines {v.lines_seen}\n- Paths: {v.paths_seen}\n"
                f"- Removal: {v.removed_commit or '-'} -> {v.removal_mechanism}\n"
                f"- [code at introduction]({v.link_introduced}) | [code last seen]({v.link_last_seen})"
                + (f" | [removal commit diff]({v.link_removal_diff})" if v.link_removal_diff else "") + "\n\n")
print(f"Manual sample: {len(V)} issues -> results/manual_validation_sample.md")

# ---------------- (3) event-level agreement + why identities differ
ev = []
Fs = F[F.tool == "sonarqube"].copy()
Hs = H[H.tool == "sonarqube"]
for repo, f in Fs.groupby("repo"):
    k = f.groupby("sonar_key").snapshot.min().astype(int).value_counts()
    o = Hs[Hs.repo == repo].introduced_snapshot.astype(int).value_counts()
    idx = k.index.union(o.index)
    k, o = k.reindex(idx, fill_value=0), o.reindex(idx, fill_value=0)
    ev.append({"repo": repo, "sonar_new_keys": int(k.sum()), "tracker_introductions": int(o.sum()),
               "event_agreement_pct": round(100 * (1 - (k - o).abs().sum() / max(k.sum(), o.sum(), 1)), 1)})
reasons = {}
for iid, f in Fs.sort_values(["issue_id", "snapshot"]).groupby("issue_id"):
    prev = None
    for _, r in f.iterrows():
        if prev is not None and r.sonar_key != prev.sonar_key:
            why = ("file renamed or moved (tracker followed git rename)" if r.path != prev.path else
                   "identical flagged code, SonarQube re-keyed it" if (r.code == prev.code and r.code) else
                   "flagged line edited, same rule and message")
            key = (r.repo, why)
            reasons[key] = reasons.get(key, 0) + 1
        prev = r
EV = pd.DataFrame(ev)
RS = pd.DataFrame([{"repo": k[0], "reason": k[1], "n": v} for k, v in reasons.items()])
EV.to_csv(R / "validation_event_agreement.csv", index=False)
RS.to_csv(R / "validation_disagreement_reasons.csv", index=False)
print(EV.to_string(index=False))
if len(RS):
    print(RS.groupby("reason").n.sum())
