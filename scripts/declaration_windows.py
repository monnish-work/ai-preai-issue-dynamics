"""
declaration_windows.py - observation windows aligned with documented AI use (DATASET.md, section 6).

For every AI-declared repository: the first commit (history of the analysed commit)
(any parent line, oldest first) whose diff adds or removes a line matching an AI-declaration pattern (git log -G, case-insensitive), and the first sampled
commit at or after it (start_index). Each Pre-AI partner gets the same start_index (same sampled positions).
Pairs with fewer than MIN_WINDOW analysed commits in the AI-declared window are not written to paired_windows.csv.

Usage:  python scripts/declaration_windows.py <raw_dir> [<raw_dir> ...]
        e.g. python scripts/declaration_windows.py data/raw_phaseC data/raw_phaseD
Input : <raw_dir>/<repo>/selection.json (sampled commits), repos/<repo>, data/study_repos_phase*.csv (pairs)
Output: data/ai_declaration_windows.csv, data/paired_windows.csv
"""
import csv, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERN = (r"(generated|written|created|code)[[:space:]]+(by|with|using|from)[[:space:]]+(an[[:space:]]+)?"
           r"(chatgpt|github[[:space:]]+copilot|copilot|claude|gpt-?[34]|cursor|openai|codex|gemini|llm|ai)"
           r"|ai-generated|llm-generated")


MIN_WINDOW = 5   # pairs whose AI-declared window has fewer analysed commits are left out of the paired analysis


def git(repo, *a):
    return subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


pairs = {}
for f in sorted((ROOT / "data").glob("study_repos_phase*.csv")):
    for r in csv.DictReader(open(f, encoding="utf-8")):
        pairs[r["repo"]] = (r["group"], r["match_id"])

sel = {}
for raw in sys.argv[1:]:
    for d in sorted(Path(raw).iterdir()):
        if (d / "selection.json").exists():
            s = json.loads((d / "selection.json").read_text(encoding="utf-8"))
            sel[s["repo"]] = s["commits"]

ai_rows, start_by_pair = [], {}
for repo, (grp, mid) in pairs.items():
    if grp != "AI" or repo not in sel:
        continue
    rdir = ROOT / "repos" / repo.replace("/", "__")
    head = sel[repo][-1]
    hits = git(rdir, "log", "--reverse", "--diff-merges=first-parent", "-i", "-E", "-G", PATTERN, "--format=%H%x09%ad%x09%s",
               "--date=short", head, "--", "*.py").splitlines()
    if not hits:
        print("no declaration commit found:", repo); continue
    h, date, subj = hits[0].split("\t", 2)
    # first sampled commit that contains the declaration commit in its history
    contains = lambda c: subprocess.run(["git", "merge-base", "--is-ancestor", h, c], cwd=rdir).returncode == 0
    start = next((i + 1 for i, c in enumerate(sel[repo]) if contains(c)), len(sel[repo]))
    ai_rows.append({"repo_dir": repo.replace("/", "__"), "repo": repo, "first_declaration_commit": h[:10],
                    "first_declaration_date": date, "commit_subject": subj[:70], "start_index": start,
                    "commits_in_window": len(sel[repo]) - start + 1, "match_id": mid})
    start_by_pair[mid] = (start, repo)

with open(ROOT / "data" / "ai_declaration_windows.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(ai_rows[0])); w.writeheader(); w.writerows(ai_rows)
rows = []
for repo, (grp, mid) in pairs.items():
    if mid in start_by_pair and repo in sel and len(sel[start_by_pair[mid][1]]) - start_by_pair[mid][0] + 1 >= MIN_WINDOW:
        st, ai = start_by_pair[mid]
        rows.append({"repo_dir": repo.replace("/", "__"), "repo": repo, "start_index": st, "pair": mid,
                     "reason": "first AI declaration" if grp == "AI" else f"same relative position as {ai}"})
with open(ROOT / "data" / "paired_windows.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in ai_rows:
    print(f"{r['match_id']:4} {r['repo']:50} {r['first_declaration_date']}  start {r['start_index']:2}  ({r['commits_in_window']} commits)")
