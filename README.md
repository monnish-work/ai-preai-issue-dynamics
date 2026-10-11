# Issue Dynamics in AI-Assisted vs. Pre-AI Software

Individual Study, 2026 · Monnish Sayi Reddy Peta

This repository contains a longitudinal study of static-analysis issues in Python repositories. It compares **AI-assisted** repositories, whose source files explicitly declare AI-generated code, with matched **Pre-AI** repositories, whose development ended before 2022. Rather than counting warnings at one point in time, it follows each warning across the Git history: when it is **introduced**, how long it **persists**, and how it is **removed**.

- **RQ1 Introduction:** are maintainability, reliability and security issues introduced at different rates?
- **RQ2 Persistence:** do issues survive for different lengths of time?
- **RQ3 Remediation:** are security issues removed faster than other issues, and does this differ between the groups?

## Where to find what

| You are looking for | Location |
|---|---|
| The 10 repositories, matching criteria, and how "AI-assisted" was determined | [`docs/DATASET.md`](docs/DATASET.md) · [`data/dataset_manifest.csv`](data/dataset_manifest.csv) |
| Tracker method, validation and failure cases | [`docs/TRACKER_VALIDATION.md`](docs/TRACKER_VALIDATION.md) |
| Issue tracker | [`scripts/track.py`](scripts/track.py) |
| Analysis scripts | [`scripts/`](scripts/): search, scanning, tracking, validation, analysis |
| Web application (Issue Lifelines) | [`app/`](app/) |
| Raw analyzer output (SonarQube + Semgrep, every analysed commit) | [`data/archives/raw_main_study.zip`](data/archives/), [`raw_pilot.zip`](data/archives/) |
| Tracker output (findings, issue histories, match log) | [`data/archives/derived_*.zip`](data/archives/) · [`data/issue_histories_main_study.csv`](data/issue_histories_main_study.csv) (one row per issue) |
| Result tables and figures | [`results_phaseC/`](results_phaseC/) (main study), [`results/`](results/) (pilot) |
| Candidate search results and search log | [`data/candidates/`](data/candidates/) |
| Exact tool versions and frozen Semgrep rules | [`tool_versions.txt`](tool_versions.txt), [`rules/`](rules/) (with SHA-256) |

## Study design in brief

| Item | Choice |
|---|---|
| AI group | Explicit attribution comments in source files, checked by hand; ≥ 2 % of `.py` files declared and ≥ 2 files |
| Pre-AI group | Last push before 2022-01-01; not a fork or archived; ≥ 10 stars; licence |
| Matching | Python; size (LOC); popularity (stars); ≥ 60 non-merge commits; domain where possible |
| Commit sampling | Pilot: last 30 non-merge commits. Main study: 30 non-merge commits evenly spaced over the whole history. The same rule applies to both groups |
| Analyzers | SonarQube Community Build 26.8 (maintainability, reliability); Semgrep CE 1.178.0 with frozen `p/python` + `p/security-audit` (security) |
| Measures | Introductions and removals per KLOC and per commit; lifetime in analysed commits and in days; right-censoring for open issues; issues present at the first commit treated as baseline |
| Statistics | Kaplan–Meier curves, log-rank test (issue level), Mann–Whitney U and Cliff's δ (repository level) |

## Main study results (5 AI-assisted + 5 Pre-AI, 300 analysed commits)

| Measure (repository level) | AI median | Pre-AI median | Mann–Whitney p | Cliff's δ |
|---|---:|---:|---:|---:|
| Issues introduced per KLOC | 56.5 | 108.4 | 0.151 | −0.60 |
| Issues removed per KLOC | 32.3 | 58.3 | 0.222 | −0.52 |
| Median issue lifetime (analysed commits) | 7.5 | 6.0 | 0.486 | 0.38 |

- Pooled over all 5,592 issues introduced in the window, AI-assisted issues survive longer (Kaplan–Meier median 10 vs 7 analysed commits, log-rank p < 0.001). Issues within a repository are not independent, so the repository-level tests above are the main result, and they are not significant with five repositories per group.
- 57 % of removals in AI-assisted repositories and 33 % in Pre-AI repositories happened because the file was deleted, not because the flagged code was edited.
- Security findings are rare (24 AI, 52 Pre-AI introduced), so RQ3 cannot be answered with this sample.

## Running it (Windows; everything stays inside the project folder)

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\setup.ps1          # once: portable Git, Python, Semgrep, Java, SonarQube, SonarScanner
.\run_app.ps1        # web app at http://localhost:5000 (uses app/study.db)
```

To reproduce the analysis from the raw data, extract the archives into `data/` (`raw_pilot.zip` → `data/raw`, `raw_main_study.zip` → `data/raw_phaseC`). Clone the analysed repositories with `python scripts/scan_repos.py --repos data/study_repos_phaseC.csv --mode spread --out data/raw_phaseC`; commits already present are skipped. Then run `.\run_pipeline.ps1`, which runs tracking, validation and analysis and rebuilds the app database.

| Step | Script | Output |
|---|---|---|
| Find candidates | `scripts/find_candidates.py`, `scripts/find_preai_pool.py` (need `GITHUB_TOKEN`) | `data/candidates/` |
| Scan commits | `scripts/scan_repos.py` | `data/raw*/<repo>/<NNN_commit>/` (`semgrep.json`, `sonar_issues.json`, `sonar_measures.json`, `meta.json`) |
| Track issues | `scripts/track.py [phaseC]` | `data/derived*/` |
| Validate tracker | `scripts/validate.py [phaseC]` | `results*/validation_*.csv`, manual sample |
| Analyse | `scripts/analyze.py [phaseC]` | `results*/` tables and figures |
| Build app database | `app/database.py` | `app/study.db` |

## Web application

*Issue Lifelines* (Flask + SQLite, plain JavaScript charts) has these pages:

- **About:** design and tool versions.
- **Results:** RQ1–RQ3, with Kaplan–Meier curves, rates and removal mechanisms.
- **Compare projects:** any AI project against any Pre-AI project.
- **Issue explorer:** all tracked issues, each with its lifeline and links to the code on GitHub.
- **Tracker validation:** agreement with SonarQube, and a manual-check form that shows the code before, during and after each issue's life.
- **Dataset** and **Limitations.**
