# Issue tracker: method, validation and failure cases

This document explains how the tracker follows a static-analysis finding across commits, how it was validated, and which failure cases were found. Each failure case states what we changed or how it is reported.
Code: [`scripts/track.py`](../scripts/track.py) (tracking), [`scripts/validate.py`](../scripts/validate.py) (validation).

## 1. How the tracker matches findings

Findings are compared between consecutive analysed commits of the same repository, separately for each tool (SonarQube, Semgrep). Line numbers alone are not used as identity, because they move when code changes.

1. **Rename mapping.** File paths of the earlier commit are mapped through Git rename detection (`git diff -M`).
2. **Exact match.** Same rule, same file, same normalised flagged code (whitespace and trailing comments removed). An occurrence index separates repeated identical findings.
3. **Context match.** Same rule and same flagged code, but at a different position.
4. **Message match.** Same rule and same message. The earlier line is mapped into the new file with a line diff (`difflib`), and the nearest candidate within 15 lines is chosen.
5. Anything left unmatched is **introduced** (new finding) or **removed** (old finding). When two candidates are equally close, the match is logged as **ambiguous** in `match_log.csv` instead of being forced silently.

For each removal we record a **mechanism**: `file_deleted` (the file no longer exists), `code_changed` (the flagged code is no longer present) or `code_still_present` (the code is still there but the warning disappeared).

**How matches were made (main study, 54,263 matches):** 89 % exact, 11 % message, 0 % context; 4 ambiguous.

## 2. Validation against SonarQube's own issue tracking

SonarQube keeps its own internal identity (issue key) for each finding across analyses. This gives an independent reference for comparison. Semgrep has no comparable identity in the Community Edition.

- **Event agreement:** per analysed commit, the number of new SonarQube issue keys compared with the tracker's introductions.
- **Identity agreement:** the share of findings where both methods agree on which earlier finding is the same issue.

| Data set | Repository | SonarQube new keys | Tracker introductions | Event agreement | Identity agreement |
|---|---|---:|---:|---:|---:|
| Pilot | pachterlab/edgePython | 463 | 462 | 99.4 % | 98.9 % |
| Pilot | dhlab-epfl/dhSegment | 202 | 197 | 97.5 % | 97.5 % |
| Main | pachterlab/edgePython | 463 | 462 | 99.4 % | 98.9 % |
| Main | temporalecologylab/TreeRings | 357 | 352 | 98.0 % | 95.8 % |
| Main | mit-acl/tcaff | 1,030 | 969 | 93.1 % | 90.5 % |
| Main | binsync/declib | 561 | 528 | 92.3 % | 91.6 % |
| Main | hanyas/sds | 1,043 | 922 | 88.4 % | 88.6 % |
| Main | jaxleyverse/jaxley | 442 | 383 | 85.3 % | 79.9 % |
| Main | TaylorResearchLab/scedar | 677 | 563 | 81.7 % | 53.6 % |
| Main | initc3/HoneyBadgerMPC | 1,142 | 901 | 78.9 % | 81.0 % |
| Main | getavalon/core | 764 | 527 | 69.0 % | 71.9 % |
| Main | jsosa/LFPtools | 661 | 433 | 65.5 % | 68.1 % |

Agreement is high in the pilot (consecutive commits) and lower in the main study, where sampled commits are far apart. SonarQube always reports more new issues than the tracker. Analysis of all 1,340 identity disagreements in the main study:

| Reason for disagreement | Count | Interpretation |
|---|---:|---|
| File renamed or moved | 794 (59 %) | The tracker follows the Git rename; SonarQube starts a new issue. The tracker is more plausible here. |
| Flagged line edited, same rule and message | 353 (26 %) | Ambiguous. Either answer is defensible. |
| Identical flagged code, SonarQube assigned a new key | 193 (14 %) | Mostly repeated identical warnings (e.g. several `pytest.raises(Exception)` in one test file) whose identities can be swapped. Counts are unaffected. |

## 3. Failure cases

| # | Failure case | How it was found | Effect | Resolution |
|---|---|---|---|---|
| FC1 | **Wrong match after code inserted above an issue.** Nearest-line matching paired a finding with a different warning of the same rule when lines shifted. Example: in `dh_segment/io/PAGE.py` (dhSegment), a `separator_regions` finding moved from line 652 to line 722; it was matched to a new finding at line 449 and its true continuation was counted as "introduced". | Disagreement with SonarQube keys in the pilot | False introductions and removals | **Fixed.** Line numbers are mapped through a diff before nearest-line matching, with a 15-line limit. dhSegment identity agreement rose from 91.6 % to 97.5 %. |
| FC2 | **Generated code counted as source.** dhSegment committed a `build/` copy of its own package and later deleted it. | Introduction spike in pilot (Python LOC doubled from about 5,000 to 10,000) | 146 fake issues introduced and removed | **Fixed.** `build/`, `dist/`, `vendor/`, `site-packages/`, `*.egg-info/` and similar folders are excluded from findings and LOC in both groups. This also removed vendored libraries in getavalon/core (LOC 48k → 14.5k). |
| FC3 | **Renamed files.** A package rename (e.g. `scxplit/` → `scedar/` in scedar) changes every path. | SonarQube comparison | Without rename detection, every issue in the file would be removed and re-introduced | **Handled** by Git rename mapping. This is the main source of disagreement with SonarQube (794 cases), where SonarQube itself loses the issue. |
| FC4 | **Identical twin warnings.** Several identical findings in one file (same rule, same code). | Identity disagreement analysis | Identities can swap between twins | **Reported, not fixed.** Introduction and removal counts are not affected; only individual lifelines of twins can be exchanged. |
| FC5 | **Edited flagged line.** The flagged line changes but the same rule and message remain. | Identity disagreement analysis | Same issue or a new issue: ambiguous | **Reported.** Matched by message within 15 mapped lines; 353 cases in the main study. |
| FC6 | **Removal mechanism misclassified.** For multi-line findings, the check for "is the flagged code still present?" compared the whole multi-line block. A finding whose line still existed was labelled `code_changed`. Example: issue #1891 (hanyas/sds, `python:S125` commented-out code). The comment line is still present after removal, so the correct label is `code_still_present`. | Manual validation (section 4) | Overstates `code_changed`, understates `code_still_present` | **Open.** To fix: compare the first flagged line, then recompute mechanism shares. |
| FC7 | **Failed SonarQube analyses.** 7 of 360 analysed commits (2 pilot, 5 main) failed in SonarQube's background processing. | Scan log | A gap in the SonarQube series | **Handled.** The commit is skipped for SonarQube only, and histories are bridged across the gap (marked as hatched cells in the app). Semgrep results for those commits are kept. |
| FC8 | **Sampling gaps.** In the main study, sampled commits can be months apart. | Design limitation | Short-lived issues between two sampled commits are never seen. Removal is attributed to the next sampled commit, not the actual one. | **Reported.** Lifetimes are given in analysed commits as well as days. |
| FC9 | **Different file coverage of the two tools.** Semgrep CE skips test folders by default (`.semgrepignore`); SonarQube analyses all `.py` files. | Inspection of Semgrep output | Security findings in tests are not counted | **Reported.** Applies equally to both groups. |

## 4. Manual validation of 10 issue histories

Ten histories were sampled from the main study, stratified by group and outcome (seed 42): removed by code change, removed by other mechanism, moved, and still open. Each was checked against the source at the introduction commit, the last commit where it was seen, and the first commit after removal.

| Issue | Repository | Rule | Introduction | Persistence | Removal (tracker label → check) |
|---|---|---|---|---|---|
| #3836 | jaxleyverse/jaxley | python:S8510 shadowed loop variable | ✔ `for i, comp_index in enumerate(inds):` at L1209 | ✔ | code_changed → ✔ line changed |
| #3654 | jaxleyverse/jaxley | python:S2638 method signature | ✔ `def compute_current(self, u, pre_voltage, post_voltage, params):` L44 | ✔ | code_changed → ✔ signature changed (`u` → `states`) |
| #4647 | mit-acl/tcaff | python:S5797 constant condition | ✔ `if False:` L249 | ✔ moved to L248 | file_deleted → ✔ file missing |
| #946 | binsync/declib | python:S1135 TODO | ✔ L1828 | ✔ moved to L2234 over 6 sightings | still open (no removal) |
| #5271 | mit-acl/tcaff | python:S117 naming | ✔ L65 | ✔ | still open (no removal) |
| #1891 | hanyas/sds | python:S125 commented-out code | ✔ L368 | ✔ moved to L384 | code_changed → ✘ line still present (FC6) |
| #2947 | initc3/HoneyBadgerMPC | python:S117 naming | ✔ `Poly = polynomialsOver(Fp)` L207 | ✔ moved to L234 | code_changed → ✔ line changed |
| #140 | TaylorResearchLab/scedar | python:S125 commented-out code | ✔ L549 | ✔ moved to L650 | file_deleted → ✔ file missing |
| #3333 | initc3/HoneyBadgerMPC | python:S112 generic exception | ✔ `raise Exception(…)` L89 | ✔ moved to L95 | still open (no removal) |
| #4254 | jsosa/LFPtools | python:S6734 `inplace=True` | ✔ L443 | ✔ moved to L495 | still open (no removal) |

**Result:** introduction correct in 10 of 10; persistence (same code followed across moves) correct in 10 of 10; removal mechanism correct in 5 of 6 removed issues. The single error is FC6.

The sample, with links to the code on GitHub, is in [`results_phaseC/manual_validation_sample.md`](../results_phaseC/manual_validation_sample.md). The web app shows the code before, during and after each issue's life (page **Tracker validation → Show code**).

## 5. Files

| File | Content |
|---|---|
| `results*/validation_sonar_agreement.csv` | Identity agreement per repository |
| `results_phaseC/validation_event_agreement.csv` | Event agreement per repository |
| `results_phaseC/validation_disagreement_reasons.csv` | Reasons for disagreement per repository |
| `results*/validation_match_methods.csv` | Matches by method, with ambiguous counts |
| `data/archives/derived_*.zip` → `match_log.csv` | Every matching decision (method, ambiguity) |
