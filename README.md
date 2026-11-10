# Issue Dynamics in AI-Declared vs. Pre-AI Software

Individual Study, 2026 · Monnish Sayi Reddy Peta

This repository contains a longitudinal study of static-analysis issues in Python repositories. It compares **AI-declared** repositories, whose source files explicitly declare AI-generated code, with matched **Pre-AI** repositories, whose development ended before 2022. Rather than counting warnings at one point in time, it follows each warning across the Git history: when it is **introduced**, how long it **persists**, and how it is **removed**. Quality is measured with the four ISO/IEC 25010 attributes used in the professor's replication package: maintainability, reliability, security and performance efficiency.

- **RQ1 Introduction:** are maintainability, reliability, security and performance-efficiency issues introduced at different rates?
- **RQ2 Persistence:** do issues survive for different lengths of time?
- **RQ3 Remediation:** are security issues removed faster than other issues, and does this differ between the groups?

## What changed in version 3 (10 November 2026)

The dataset was extended from 5 to **40 matched pairs** (25 strict-rule pairs, 15 relaxed-rule pairs, all marked), scanned with the same tools and analysed with the same scripts ([`docs/DATASET.md`](docs/DATASET.md) §7–8). Results: [`docs/RESULTS.md`](docs/RESULTS.md); short overview for the supervisor: [`docs/SUMMARY.md`](docs/SUMMARY.md).

## What changed in version 2 (November 2026)

| Request (October review and 9 November recap) | Where it is addressed |
|---|---|
| Repository-level comparison as the main result, with multiple-comparison correction | [`docs/ANALYSIS.md`](docs/ANALYSIS.md) §3–4 (Mann–Whitney, Cliff's δ, Holm over 40 tests) |
| Clear definitions of lifetime, censoring, baseline issues; reconciled removal counts | [`docs/ANALYSIS.md`](docs/ANALYSIS.md) §1, `results_*/v2/count_reconciliation.csv` |
| Tracker fixes (renames/moves, repeated warnings, multi-line findings) and their measured impact | [`docs/TRACKER_VALIDATION.md`](docs/TRACKER_VALIDATION.md) §1–2, `results_phaseC/tracker_fix_impact*.csv` |
| FC6 fixed and removal mechanisms recomputed; correction of issue #1891 | [`docs/TRACKER_VALIDATION.md`](docs/TRACKER_VALIDATION.md) §4–5 |
| scedar / getavalon disagreement with SonarQube explained | [`docs/TRACKER_VALIDATION.md`](docs/TRACKER_VALIDATION.md) §3 |
| Observation window aligned with documented AI use | [`docs/DATASET.md`](docs/DATASET.md) §6, `data/ai_declaration_windows.csv`, `data/paired_windows.csv` |
| "AI-assisted" renamed "AI-declared" | everywhere (docs, results, app) |
| Four ISO/IEC 25010 attributes, density per KLOC, rule mapping and tools of the replication package, Ruff for performance | [`docs/ANALYSIS.md`](docs/ANALYSIS.md) §2, [`mappings/`](mappings/), `scripts/run_ruff.py` |
| Process metrics (commits per author, distinct authors, developer experience) | `scripts/process_metrics.py`, [`docs/ANALYSIS.md`](docs/ANALYSIS.md) §4.4 |
| Extend the dataset towards 83 + 83 pairs | 40 + 40 pairs analysed ([`docs/DATASET.md`](docs/DATASET.md) §7–8, [`docs/RESULTS.md`](docs/RESULTS.md)); what limits further growth: [`docs/FEASIBILITY.md`](docs/FEASIBILITY.md) |

## Where to find what

| You are looking for | Location |
|---|---|
| The repositories, matching criteria, how "AI-declared" was determined, observation windows, candidate review | [`docs/DATASET.md`](docs/DATASET.md) · [`data/dataset_manifest.csv`](data/dataset_manifest.csv) |
| Definitions, quality model and statistics | [`docs/ANALYSIS.md`](docs/ANALYSIS.md) |
| Current results (all pairs, generated from the result files) | [`docs/RESULTS.md`](docs/RESULTS.md) |
| Tracker method, validation and failure cases | [`docs/TRACKER_VALIDATION.md`](docs/TRACKER_VALIDATION.md) |
| Further extension (towards 83 pairs) | [`docs/FEASIBILITY.md`](docs/FEASIBILITY.md) |
| Scripts | [`scripts/`](scripts/): search, scanning, Ruff, tracking, validation, analysis, process metrics |
| Rule-to-attribute mappings (from the replication package) | [`mappings/`](mappings/) |
| Web application (Issue Lifelines) | [`app/`](app/) |
| Raw analyzer output (SonarQube, Semgrep, Ruff; every analysed commit) | [`data/archives/`](data/archives/): `raw_main_study.zip` (M1–M5), `raw_extension.tar.xz` (M6–M41), `raw_pilot.zip` |
| Tracker output (findings, issue histories, match log) | [`data/archives/derived_all.tar.xz`](data/archives/) · [`data/issue_histories_all_pairs.csv.xz`](data/) (one row per issue, all pairs, whole history) |
| Result tables | [`results_ext_paired/v2/`](results_ext_paired/v2/) (**main result**, all pairs, AI-declaration windows), [`results_ext/v2/`](results_ext/v2/) (whole history), `v2_sens_*` folders (sensitivity), `results_phaseC*/` (first 5 pairs, October/November report), [`results/`](results/) (pilot) |
| Exact tool versions and frozen Semgrep rules | [`tool_versions.txt`](tool_versions.txt), [`rules/`](rules/) (with SHA-256) |

## Study design in brief

| Item | Choice |
|---|---|
| AI-declared group | Explicit attribution comments in source files, checked by hand; ≥ 2 % of `.py` files declared and ≥ 2 files |
| Pre-AI group | Last push before 2022-01-01; not a fork or archived; ≥ 10 stars; licence |
| Matching | Python; size (LOC); popularity (stars); ≥ 60 non-merge commits; domain where possible |
| Commit sampling | 30 non-merge commits evenly spaced over the first-parent history, same rule in both groups (pilot: last 30) |
| Observation window (main result) | AI-declared: from the first commit that adds an AI declaration. Pre-AI partner: the same sampled positions of its own history. Whole history kept as sensitivity analysis |
| Analyzers | SonarQube Community Build 26.8 (maintainability, reliability); Semgrep CE 1.178.0, frozen `p/python` + `p/security-audit` (security); Ruff 0.17.4 PERF rules (performance efficiency) |
| Measures | Introductions and removals per KLOC (and per commit); density per KLOC (last commit and mean); share removed; lifetime in analysed commits and days with right-censoring; baseline issues excluded from introductions; removal mechanism; process metrics |
| Statistics | Repository level (main): exact Mann–Whitney U, Cliff's δ, Holm correction. Supporting: Kaplan–Meier, log-rank pooled and stratified by matched pair |

<!-- RESULTS-START -->
## Main results (40 AI-declared + 40 Pre-AI repositories)

Full tables: [`docs/RESULTS.md`](docs/RESULTS.md) (generated from the result files). 25 pairs meet the strict selection rule; the others were added with relaxed rules and are marked (every test is repeated on the strict pairs only).

Repository level, all four attributes, AI-declaration windows (34 pairs):

| Measure | AI-declared median | Pre-AI median | p | p (Holm) | Cliff's δ |
|---|---:|---:|---:|---:|---:|
| Introduced per KLOC | 14.17 | 41.87 | 0.019 | 0.563 | -0.33 |
| Removed per KLOC | 4.21 | 17.26 | 0.003 | 0.109 | -0.41 |
| Density at last commit | 16.09 | 28.41 | 0.002 | 0.073 | -0.43 |
| Share of introduced issues removed | 0.13 | 0.25 | 0.034 | 0.951 | -0.30 |

- **Repository level (main result):** 3 of 80 repository-level tests are significant after Holm correction (both windows). Introductions per KLOC: AI-declared 40.44 vs Pre-AI 82.91 over the whole history (δ = -0.41).
- **Survival (supporting):** pooled over all introduced issues, log-rank p = < 0.001 (whole history) and < 0.001 (AI windows); stratified by matched pair p = < 0.001 and < 0.001. Kaplan–Meier median 17 vs 23 analysed commits (whole history).
- **How issues disappear:** 41 % of removals in AI-declared repositories are whole-file deletions, against 48 % in Pre-AI repositories (whole history).
- **Process metrics:** developer experience (days since an author's first commit, per author) 167 vs 356 days (p = < 0.001, Holm < 0.001).
- **Security** issues remain rare, so RQ3 has low power.

<!-- RESULTS-END -->

## Running it on macOS or Linux

```bash
./setup_mac.sh        # once: Python environment in .venv (needs python3 and git)
./run_app.sh          # web app at http://localhost:5000
./run_pipeline.sh     # optional: re-computes every result from the archived raw scans (about 1 hour)
./setup_mac.sh --with-scanners   # only to re-scan repositories: Semgrep, Ruff, SonarQube, SonarScanner (needs Java 21)
```

## Running it (Windows; everything stays inside the project folder)

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\setup.ps1          # once: portable Git, Python, Semgrep, Java, SonarQube, SonarScanner
.\run_app.ps1        # web app at http://localhost:5000 (uses app/study.db)
```

To reproduce the analysis from the raw data, run `python scripts/unpack_archives.py` (extracts every archive into `data/`; `app/study.db` is unpacked automatically by `run_app.ps1`). Clone the analysed repositories with `python scripts/scan_repos.py --repos data/study_repos_phaseC.csv --mode spread --out data/raw_phaseC` (and the same for `study_repos_phaseD.csv`, `study_repos_phaseE1.csv`, `study_repos_phaseE2.csv` with `--out data/raw_phaseD` / `data/raw_phaseE`); commits already present are skipped. Then run `.\run_pipeline.ps1`, which runs Ruff windows, tracking, validation, both analyses with all sensitivity runs, the process metrics and the report, and rebuilds the app database.

| Step | Script | Output |
|---|---|---|
| Find candidates | `scripts/find_candidates.py`, `scripts/find_preai_pool.py`; wider search `run_wide_search.ps1` → `scripts/find_candidates_wide.py` (ask for a GitHub token, never stored) | `data/candidates/` |
| Scan commits | `scripts/scan_repos.py` | `data/raw*/<repo>/<NNN_commit>/` (`semgrep.json`, `sonar_issues.json`, `sonar_measures.json`, `meta.json`) |
| Performance findings | `scripts/run_ruff.py phaseC` | `ruff.json` in each commit folder |
| Track issues | `scripts/track.py phaseC` (`WINDOW_FILE`, `OUT_TAG`, `FIXES` options) | `data/derived*/` |
| Tracker fix impact | `scripts/fix_impact.py` | `results_phaseC/tracker_fix_impact*.csv` |
| Validate tracker | `scripts/validate.py <tag>` | `results*/validation_*.csv` |
| Analyse | `scripts/analyze_v2.py <tag>` (`LOC`, `MAPPING` options); figures: `scripts/analyze.py <tag>` | `results*/v2/`, `results*/figures/` |
| Process metrics | `scripts/process_metrics.py <tag>` | `results*/v2/process_*.csv` |
| Build app database | `app/database.py` | `app/study.db` |

## Web application

*Issue Lifelines* (Flask + SQLite, plain JavaScript charts) has these pages:

- **About:** design, definitions and tool versions.
- **Results:** RQ1–RQ3 with Kaplan–Meier curves, rates and removal mechanisms; all repository-level tests with Holm correction; pair-stratified survival; count reconciliation; process metrics.
- **Compare projects:** any AI-declared project against any Pre-AI project.
- **Issue explorer:** all tracked issues, each with its lifeline and links to the code on GitHub.
- **Tracker validation:** agreement with SonarQube, and a manual-check form that shows the code before, during and after each issue's life.
- **Dataset** and **Limitations.**

Switch between the data sets (main result with AI-declaration windows, whole history, pilot) with **Data set** in the sidebar.
