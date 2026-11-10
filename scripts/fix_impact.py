"""fix_impact.py - measure the impact of each tracker fix on counts and on agreement with SonarQube.
Reads data/derived_phaseC_<variant>/ for variants none, rename, twins, multiline, all.
Writes results_phaseC/tracker_fix_impact.csv (per repository) and tracker_fix_impact_summary.csv."""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PRIMARY = {("sonarqube", "maintainability"), ("sonarqube", "reliability"), ("semgrep", "security")}
VARIANTS = ["none", "rename", "twins", "multiline", "all"]
rows = []
for v in VARIANTS:
    D = ROOT / "data" / f"derived_phaseC_{v}"
    H = pd.read_csv(D / "issue_histories.csv", keep_default_na=False)
    F = pd.read_csv(D / "findings.csv", keep_default_na=False, usecols=["repo", "snapshot", "issue_id", "tool", "sonar_key"])
    P = H[[(t, c) in PRIMARY for t, c in zip(H.tool, H.category)]]
    for repo, h in P.groupby("repo"):
        base = h.present_at_first_snapshot.astype(str) == "True"
        rem = h.removed_commit != ""
        mech = h[rem].removal_mechanism.value_counts()
        sq = H[(H.repo == repo) & (H.tool == "sonarqube")]
        fs = F[(F.repo == repo) & (F.tool == "sonarqube")]
        keys_per_hist = sq.sonar_keys.str.split("|").apply(len)
        key_hist = fs.groupby("sonar_key").issue_id.nunique()
        # SonarQube's own identities: a key first seen after snapshot 1 = introduction; key not seen at the last snapshot = removal
        first = fs.groupby("sonar_key").snapshot.min(); last = fs.groupby("sonar_key").snapshot.max()
        n_snap = fs.snapshot.max()
        k_new = first                                   # every key, by the snapshot where SonarQube first reports it
        o_new = sq.introduced_snapshot.astype(int)      # every tracker history, by its first snapshot
        a = k_new.value_counts(); b = o_new.value_counts(); idx = a.index.union(b.index)
        a, b = a.reindex(idx, fill_value=0), b.reindex(idx, fill_value=0)
        rows.append({"variant": v, "repo": repo, "group": h.group.iloc[0],
                     "histories": len(h), "baseline": int(base.sum()), "introduced": int((~base).sum()),
                     "removed": int(rem.sum()), "removed_in_window": int((rem & ~base).sum()),
                     "code_changed": int(mech.get("code_changed", 0)), "file_deleted": int(mech.get("file_deleted", 0)),
                     "code_still_present": int(mech.get("code_still_present", 0)),
                     "sonar_new_keys": int(len(k_new)), "tracker_sonar_introductions": int(len(o_new)),
                     "event_agreement_pct": round(100 * (1 - (a - b).abs().sum() / max(a.sum(), b.sum(), 1)), 1),
                     "identity_agreement_pct": round(100 * (1 - ((keys_per_hist > 1).sum() + (key_hist > 1).sum()) / max(1, len(key_hist))), 1)})
R = pd.DataFrame(rows)
out = ROOT / "results_phaseC"
R.to_csv(out / "tracker_fix_impact.csv", index=False)
S = R.groupby("variant").agg(introduced=("introduced", "sum"), removed=("removed", "sum"),
                             code_changed=("code_changed", "sum"), file_deleted=("file_deleted", "sum"),
                             code_still_present=("code_still_present", "sum"),
                             event_agreement_median=("event_agreement_pct", "median"),
                             identity_agreement_median=("identity_agreement_pct", "median")).reindex(VARIANTS)
S.to_csv(out / "tracker_fix_impact_summary.csv")
pd.set_option("display.width", 250)
print(S.to_string())
print(R[R.variant.isin(["none", "all"])].pivot(index="repo", columns="variant",
      values=["introduced", "removed", "event_agreement_pct", "identity_agreement_pct"]).to_string())
