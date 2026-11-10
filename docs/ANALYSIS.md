# Analysis: definitions, measures and results

This document defines every quantity used in the comparison, explains the observation windows and the quality model, and reports the results (version 2 of the analysis, November 2026).
Code: [`scripts/analyze_v2.py`](../scripts/analyze_v2.py) (issue measures and tests), [`scripts/process_metrics.py`](../scripts/process_metrics.py) (process metrics), [`scripts/run_ruff.py`](../scripts/run_ruff.py) (performance findings).
Results: `results_ext_paired/v2/` (main result, all pairs), `results_ext/v2/` (whole history); for the first five pairs `results_phaseC_paired/v2/` and `results_phaseC/v2/` (plus `results_phaseC_aligned/v2/`, AI windows only, shown for comparison).
The tables directly inside `results_*/` (e.g. `repo_level_tests.csv`) and the figures come from the first analysis script (`analyze.py`: three attributes, no Holm correction) and are kept for comparison with the October report; the `v2/` tables replace them.

## 1. Definitions

| Term | Definition |
|---|---|
| **AI-declared repository** | Its source files contain explicit statements that an AI tool generated or wrote code (see [DATASET.md](DATASET.md), section 2). |
| **Pre-AI repository** | Development ended before 2022, before modern AI coding assistants. |
| **Analysed commit** | One of the 30 sampled non-merge commits of a repository (evenly spaced over the first-parent history). Inside an observation window, only the sampled commits from the window start onwards are used. |
| **Observation window** | Main result: the AI-declared repository from the first sampled commit at or after the first commit that adds an AI declaration; the Pre-AI partner over the same sampled positions of its own history ([DATASET.md](DATASET.md), section 6). Sensitivity: the whole history. |
| **Finding** | One warning of one tool at one analysed commit. |
| **Issue (history)** | A finding followed across analysed commits by the tracker ([TRACKER_VALIDATION.md](TRACKER_VALIDATION.md)). |
| **Primary issues** | The four ISO/IEC 25010 attributes of the professor's study: Maintainability and Reliability (SonarQube), Security (Semgrep), Performance efficiency (Ruff PERF rules). "All" = their sum. SonarQube security hotspots/vulnerabilities and Semgrep non-security rules are kept in the data but are not primary. |
| **Baseline issue** | Already present at the first analysed commit of the window. Its introduction is unknown (left-censored). Excluded from introduction counts, introduction rates and lifetimes; included in "removed (all)" and in densities. |
| **Introduced issue** | First seen at analysed commit k ≥ 2 of the window. |
| **Removed issue** | Present at one analysed commit and absent at a later one; the removal commit is the first analysed commit without it. Each removal has a mechanism: `code_changed`, `file_deleted` or `code_still_present`. |
| **Right-censored issue** | Still present at the last analysed commit of the window: its full lifetime is unknown. Kaplan–Meier estimates treat it as "survived at least this long". |
| **Lifetime** | Analysed commits from introduction to removal (or to the last analysed commit, if censored). Also reported in calendar days. |
| **KLOC** | 1,000 lines of Python, counted as in the replication package (`ruff_density_delta.py`): all lines of `.py` files, generated and vendored folders excluded (`build/`, `dist/`, `vendor/`, `site-packages/`, …). Non-blank lines are used as a sensitivity check. |
| **Density** | Open primary issues per KLOC, at the last analysed commit (`density_last`) and averaged over the analysed commits (`density_mean`). |

### How the counts fit together (paired windows)

| Set | Histories | Removed | Used for |
|---|---:|---:|---|
| A. All issue histories (every tool and category) | 4,088 | 935 | `issue_histories.csv` |
| B. Primary issues (four attributes) | 4,064 | 931 | densities, "removed (all)", mechanism shares |
| — of which baseline issues | 2,089 | 482 | |
| C. Primary issues introduced in the window | 1,975 | 449 | introduction rates, lifetimes, survival curves |
| — of which right-censored | 1,526 | 0 | |

Whole history: A 6,064 / 2,911; B 6,008 / 2,875; baseline 475 / 72; C 5,533 / 2,803; right-censored 2,730. In the tracker comparison (primary SonarQube + Semgrep issues, whole history) tracker v1 counted 3,013 removals and v2 counts 2,801: 212 fewer, mostly false removals caused by file moves ([TRACKER_VALIDATION.md](TRACKER_VALIDATION.md), section 2). Adding Ruff's performance issues gives the 2,875 removals of set B ([TRACKER_VALIDATION.md](TRACKER_VALIDATION.md), section 2). Every number is regenerated in `count_reconciliation.csv`.

## 2. Quality model and tools

The mapping from rules to quality attributes follows the professor's replication package (Zenodo record 21870905, `mappings/`), which was obtained and compared rule by rule. Copies are in [`mappings/`](../mappings/).

| Attribute | Tool and version | Rules | Mapping |
|---|---|---|---|
| Maintainability | SonarQube Community Build 26.8.0.126808 | Python rules with software quality MAINTAINABILITY | SonarQube's own classification (`impacts.softwareQuality`), as in `sonar_python_rule_attribute_mapping.csv` |
| Reliability | SonarQube (same) | Python rules with software quality RELIABILITY | same |
| Security | Semgrep CE 1.178.0 | `p/python` + `p/security-audit` (frozen copies in `rules/`), security category | all Semgrep security patterns → Security (`semgrep_pattern_attribute_mapping.csv`) |
| Performance efficiency | Ruff 0.17.4 | `ruff check . --isolated --select PERF` (perflint), as in `run_ruff.py` of the package | all PERF rules → Performance efficiency (`ruff_rule_attribute_mapping.csv`) |

**Comparison with the replication package's mapping.** 89 of the SonarQube rules observed in our data (50,664 of 59,562 SonarQube findings) appear in the package's mapping, and for all of them our category equals the package's attribute: there is no disagreement. Two differences remain:

- 37 rules (6,493 findings, e.g. `python:S5958` broad `pytest.raises`, `python:S5778`) do not appear in the package's mapping, because they did not occur in its dataset. We keep SonarQube's own classification for them, which is the rule the package states ("mapped consistently with SonarQube classification").
- 9 rules that SonarQube assigns to *several* qualities (e.g. `python:S6729`, `python:S6709`; 2,405 findings) are marked "Excluded" in the package. We assign them to their highest-severity quality. The sensitivity run `MAPPING=strict` drops them exactly as the package does (`results_*/v2_sens_strict_mapping/`): no conclusion changes.

The package does not pin tool versions in its scripts (it checks the installed version at run time), so our versions are recorded in [`tool_versions.txt`](../tool_versions.txt). The package uses more Semgrep bundles (`p/owasp-top-ten`, `p/cwe-top-25`, `p/secrets`, …); our two frozen bundles are a subset, so our security counts are lower bounds. Re-running Semgrep with the extra bundles would need the laptop scan setup (about 2 hours for the 300 commits).

## 3. Statistical approach

- **Main result: repository level.** Each repository gives one value per measure (5 AI-declared vs 5 Pre-AI). Exact two-sided Mann–Whitney U test, Cliff's δ as effect size (δ > 0: higher in AI-declared). **Holm correction** over every test in the table (5 categories × 8 measures = 40 tests). Measures: introductions and removals per KLOC, the same per KLOC per analysed commit, `density_last`, `density_mean`, share of introduced issues removed in the window, and Kaplan–Meier median lifetime (only where the median is reached).
- **Supporting evidence: pooled survival.** Kaplan–Meier curves per group and the log-rank test over all issues; also a **log-rank test stratified by matched pair**, which compares AI-declared and Pre-AI issues only within each pair. Issues of one repository are not independent, so these p-values overstate certainty.
- **Process metrics** are tested in their own family (6 tests, Holm).
- With 5 repositories per group, the smallest possible exact two-sided p-value is 0.0079, and after Holm over 40 tests no difference can reach 0.05 unless the two groups separate completely in several measures. This is why the dataset was extended (40 pairs: [DATASET.md](DATASET.md), sections 7–8); with 40 per group, medium-to-large effects (|δ| ≳ 0.5) can survive the correction.
- Relaxed-rule pairs are marked in the study lists (column `tier`); `TIERS=S` repeats the analysis on the strict pairs only (`v2_sens_strict_tier/`).

## 4. Results for the first five pairs

> These tables are the results for the first five pairs (M1–M5). The current results for all pairs, produced with exactly the same scripts, are in [RESULTS.md](RESULTS.md), which is generated directly from the result files.

### 4.1 Repository level (main result, paired windows)

| Measure (all four attributes) | AI-declared median | Pre-AI median | p | p (Holm) | Cliff's δ |
|---|---:|---:|---:|---:|---:|
| Introduced per KLOC | 4.36 | 16.77 | 0.31 | 1.00 | −0.44 |
| Removed per KLOC | 6.64 | 8.15 | 0.55 | 1.00 | −0.28 |
| Introduced per KLOC per commit | 0.62 | 2.29 | 0.31 | 1.00 | −0.44 |
| Density at last commit (per KLOC) | 16.08 | 19.62 | 0.55 | 1.00 | −0.28 |
| Mean density (per KLOC) | 16.12 | 30.00 | 0.42 | 1.00 | −0.36 |
| Share of introduced issues removed | 0.03 | 0.14 | 0.69 | 1.00 | −0.24 |

No repository-level difference is significant after Holm correction, in any category (smallest raw p = 0.095: reliability density, higher in AI-declared, δ = 0.68). The same holds for the whole history (smallest raw p = 0.095) and for both sensitivity runs (strict mapping, non-blank KLOC). Direction: AI-declared repositories introduce fewer issues per KLOC than their Pre-AI partners in 3 of 5 pairs in the paired windows (4 of 5 over the whole history; M5 tcaff is the exception in both), and remove a smaller share of what they introduce in 3 of 5 pairs.

**Density per KLOC per repository and attribute** (last analysed commit; identical in both windows because the last commit is the same):

| Pair | Repository | Group | Maint. | Rel. | Sec. | Perf. | All |
|---|---|---|---:|---:|---:|---:|---:|
| M1 | pachterlab/edgePython | AI-declared | 17.45 | 0.56 | 0.00 | 0.08 | 18.08 |
| M1 | TaylorResearchLab/scedar | Pre-AI | 19.30 | 0.00 | 0.19 | 0.13 | 19.62 |
| M2 | binsync/declib | AI-declared | 11.61 | 0.26 | 0.26 | 0.48 | 12.61 |
| M2 | getavalon/core | Pre-AI | 12.91 | 0.38 | 0.06 | 0.33 | 13.68 |
| M3 | jaxleyverse/jaxley | AI-declared | 6.35 | 0.69 | 0.00 | 0.82 | 7.86 |
| M3 | initc3/HoneyBadgerMPC | Pre-AI | 11.78 | 0.47 | 1.15 | 1.20 | 14.61 |
| M4 | temporalecologylab/TreeRings | AI-declared | 14.47 | 1.03 | 0.00 | 0.57 | 16.08 |
| M4 | hanyas/sds | Pre-AI | 35.84 | 0.21 | 0.00 | 0.07 | 36.12 |
| M5 | mit-acl/tcaff | AI-declared | 87.09 | 1.48 | 0.21 | 2.11 | 90.89 |
| M5 | jsosa/LFPtools | Pre-AI | 44.63 | 0.59 | 0.00 | 0.59 | 45.81 |

The AI-declared repository has the lower total density in 4 of 5 pairs (all except M5), but a *higher reliability* density in 4 of 5 pairs.

### 4.2 Pooled survival (supporting evidence)

| Window | Category | AI-declared issues | Pre-AI issues | Log-rank p | Pair-stratified p |
|---|---|---:|---:|---:|---:|
| Paired windows | All | 599 | 1,376 | < 0.001 | < 0.001 |
| Paired windows | Maintainability | 554 | 1,319 | < 0.001 | 0.002 |
| Paired windows | Reliability | 17 | 16 | 0.030 | 0.157 |
| Paired windows | Performance | 21 | 29 | 0.50 | 0.55 |
| Whole history | All | 2,356 | 3,177 | < 0.001 | < 0.001 |
| Whole history | Reliability | 87 | 80 | < 0.001 | < 0.001 |

Issues introduced in AI-declared repositories **survive longer** (whole history: Kaplan–Meier median 12 vs 8 analysed commits; in the paired windows the AI-declared median is not reached, Pre-AI 13), also when the comparison is restricted to within matched pairs. Security has too few issues (7 vs 12 in the paired windows) for any conclusion.

### 4.3 How issues disappear

| Window | Group | code_changed | file_deleted | code_still_present |
|---|---|---:|---:|---:|
| Paired | AI-declared | 36 % | 54 % | 10 % |
| Paired | Pre-AI | 49 % | 37 % | 13 % |
| Whole history | AI-declared | 36 % | 55 % | 8 % |
| Whole history | Pre-AI | 62 % | 28 % | 10 % |

In AI-declared repositories most issues disappear because the whole file is deleted, not because the flagged code is fixed. In TreeRings' 5-commit declaration window, all 131 removals are file deletions (a clean-up commit).

### 4.4 Process metrics

Definitions are in the docstring of `process_metrics.py` (commits in the window, distinct authors by e-mail with bots excluded, commits per author, developer experience = days since the author's first commit in the repository, averaged over commits and over authors).

| Measure (whole history) | AI-declared median | Pre-AI median | p | p (Holm) | Cliff's δ |
|---|---:|---:|---:|---:|---:|
| Commits in window | 277 | 298 | 1.00 | 1.00 | −0.04 |
| Distinct authors | 10 | 3 | 0.22 | 0.89 | 0.52 |
| Commits per author | 28.7 | 85.5 | 0.095 | 0.57 | −0.68 |
| Dev. experience (days, per commit) | 230 | 256 | 0.69 | 1.00 | −0.20 |

AI-declared repositories tend to have more authors with fewer commits each; no difference is significant. These metrics are reported to describe the projects and as possible confounders, not as outcomes.

## 5. Threats specific to this analysis

- **Five pairs.** Low power at repository level (section 3).
- **Short declaration windows.** 5–14 analysed commits for three pairs; many baseline issues.
- **Retroactive declaration** in TreeRings ([DATASET.md](DATASET.md), section 6).
- **Sampling gaps** between analysed commits (FC8 in [TRACKER_VALIDATION.md](TRACKER_VALIDATION.md)).
- **Security coverage**: two Semgrep bundles and no test folders (FC9); security results are lower bounds.
