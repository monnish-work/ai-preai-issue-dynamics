# Issue tracker: method, validation and failure cases

This document explains how the tracker follows a static-analysis finding across commits, how it was validated, which failure cases were found, and how the three fixes requested after the October review (rename handling, repeated warnings, multi-line findings) changed the results.
Code: [`scripts/track.py`](../scripts/track.py) (tracking), [`scripts/validate.py`](../scripts/validate.py) (validation), [`scripts/fix_impact.py`](../scripts/fix_impact.py) (impact of each fix).

## 1. How the tracker matches findings (version 2)

Findings are compared between consecutive analysed commits of the same repository, separately for each tool (SonarQube, Semgrep, Ruff). Line numbers alone are never used as identity, because they move when code changes.

1. **Rename mapping.** File paths of the earlier commit are mapped through Git rename detection with a 40 % similarity threshold (`git diff -M40%`; Git's default is 50 %).
2. **Exact match.** Same rule, same file, same normalised flagged code (whitespace and trailing comments removed). When a file contains several identical findings ("twins", e.g. five `pytest.raises(Exception)` in one test file), they are paired by an **optimal assignment** (Hungarian algorithm) on the distance between the diff-mapped old line and the new line, instead of by order of appearance. Logged as `exact_twin`.
3. **Moved match.** Same rule and same flagged code in a *different* file, accepted only when the old file no longer exists in the new commit (or the new file did not exist in the old one) and exactly one candidate exists. This follows code that moved during a refactoring that Git does not detect as a rename (e.g. one module split into a package). Several candidates: logged as `moved_unresolved` and left unmatched.
4. **Message match.** Same rule and same message. The earlier line is mapped into the new file with a line diff (`difflib`), and the nearest candidate within 15 lines is chosen.
5. Anything left unmatched is **introduced** (new finding) or **removed** (old finding). Ties are logged as **ambiguous** in `match_log.csv` instead of being forced silently.

For each removal we record a **mechanism**: `file_deleted` (the file no longer exists), `code_changed` (the flagged code is no longer present) or `code_still_present` (the code is still there but the warning disappeared). For multi-line findings, "still present" means that the whole flagged block (up to 6 lines, whitespace-normalised, **comments kept**) still occurs as a contiguous run of lines in the new version of the file.

**How matches were made (whole-history data set, 56,129 decisions, all three tools):** 66 % exact, 23 % exact twins (optimal assignment), 11 % message, 0.3 % moved (155); 156 move candidates were ambiguous and left unmatched.

## 2. Impact of the three tracker fixes

Each fix was switched on alone and then together (environment variable `FIXES`), on the whole-history data set (SonarQube and Semgrep findings, 300 analysed commits). Output: [`results_phaseC/tracker_fix_impact.csv`](../results_phaseC/tracker_fix_impact.csv) (per repository) and [`tracker_fix_impact_summary.csv`](../results_phaseC/tracker_fix_impact_summary.csv).

| Variant | Introduced | Removed | code_changed | file_deleted | code_still_present | Event agreement (median) | Identity agreement (median) |
|---|---:|---:|---:|---:|---:|---:|---:|
| v1 (no fixes) | 5,592 | 3,013 | 1,481 | 1,294 | 238 | 86.9 % | 84.8 % |
| rename only | 5,385 | 2,806 | 1,471 | 1,097 | 238 | 83.4 % | 83.4 % |
| twins only | 5,588 | 3,009 | 1,479 | 1,294 | 236 | 86.7 % | 85.8 % |
| multi-line only | 5,592 | 3,013 | 1,451 | 1,294 | 268 | 86.9 % | 84.8 % |
| **all fixes (v2, used)** | **5,380** | **2,801** | **1,438** | **1,097** | **266** | 83.2 % | 84.5 % |

What each fix does to the results:

- **Rename / move handling** removes 207 false "introduce + remove" pairs. 197 of them were counted as `file_deleted`, although the file had only been moved or split (e.g. `scxplit/cluster.py` → `scedar/cluster/mirac.py`). The moved matches were checked by listing the old and new directories: all are package renames or module splits (`mindbender/` → `avalon/`, `scxplit/` → `scedar/…`, top-level scripts → `lfptools/`). Event agreement with SonarQube goes *down*, because SonarQube itself starts a new issue key when a file moves (section 3): the tracker is now further from SonarQube exactly where SonarQube is wrong.
- **Twin assignment** does not change counts (by construction) but fixes which twin is which: identity agreement rises in the repositories with many twins (scedar 53.6 % → 59.5 %, jaxley 79.9 % → 84.2 %).
- **Multi-line fix** reclassifies 30 removals from `code_changed` to `code_still_present` when applied alone (28 in the combined v2 run, where some of those removals had already disappeared through the rename fix), mostly commented-out code (`python:S125`) and long statements. This is the general FC6 problem (section 4).

**Effect on the conclusions.** The group-level picture is unchanged by the fixes: AI-declared removals are still dominated by file deletion (55 % vs 28 % in the whole history), and no repository-level test is significant after Holm correction in either version.

## 3. Validation against SonarQube's own issue tracking

SonarQube keeps its own internal identity (issue key) for each finding across analyses. This gives an independent reference. Semgrep and Ruff have no comparable identity.

- **Event agreement:** per repository, the number of new SonarQube issue keys compared with the tracker's introductions of SonarQube findings.
- **Identity agreement:** the share of SonarQube keys that are neither split over several tracker histories nor merged with another key in one history.

| Repository | Group | SonarQube new keys | Tracker introductions | Event agreement | Identity agreement |
|---|---|---:|---:|---:|---:|
| pachterlab/edgePython | AI-declared | 463 | 462 | 99.4 % | 99.4 % |
| temporalecologylab/TreeRings | AI-declared | 357 | 351 | 97.8 % | 96.6 % |
| binsync/declib | AI-declared | 561 | 522 | 91.6 % | 91.1 % |
| mit-acl/tcaff | AI-declared | 1,030 | 935 | 89.8 % | 87.6 % |
| hanyas/sds | Pre-AI | 1,043 | 866 | 83.0 % | 86.2 % |
| jaxleyverse/jaxley | AI-declared | 442 | 374 | 83.3 % | 82.8 % |
| initc3/HoneyBadgerMPC | Pre-AI | 1,142 | 885 | 77.5 % | 80.2 % |
| TaylorResearchLab/scedar | Pre-AI | 677 | 514 | 74.4 % | 60.1 % |
| jsosa/LFPtools | Pre-AI | 661 | 428 | 64.8 % | 67.3 % |
| getavalon/core | Pre-AI | 764 | 495 | 64.8 % | 71.1 % |

SonarQube always reports more new issues than the tracker. Reasons for all 1,487 identity disagreements ([`validation_disagreement_reasons.csv`](../results_phaseC/validation_disagreement_reasons.csv)):

| Reason for disagreement | Count | Interpretation |
|---|---:|---|
| File renamed or moved | 999 (67 %) | The tracker follows the rename/move; SonarQube starts a new issue key. The tracker is more plausible. |
| Flagged line edited, same rule and message | 355 (24 %) | Ambiguous: either answer is defensible. |
| Identical flagged code, SonarQube re-keyed it | 133 (9 %) | Twin warnings; counts unaffected. |

### Why scedar and getavalon disagree most

The two lowest-agreement repositories are both Pre-AI and both went through large restructurings; the disagreement is a property of their history, not a tracker failure that favours one group.

- **getavalon/core** (event 64.8 %, identity 71.1 %): the project was renamed from *mindbender* to *avalon* during the observed history, so the whole package moved (`mindbender/` → `avalon/`, `mindbender/maya/` → `avalon/maya/`), and several tools were renamed (`tools/cbloader` → `tools/loader`, `tools/cbsceneinventory` → `tools/sceneinventory`). 249 of the 277 disagreements are such moves: the tracker keeps the issue, SonarQube creates a new key. The low *event* agreement has the same cause: each move creates a burst of "new" SonarQube keys that the tracker does not count as introductions.
- **TaylorResearchLab/scedar** (event 74.4 %, identity 60.1 %, the lowest): the package `scxplit/` was renamed to `scedar/` *and* split into sub-packages (`scedar/eda`, `scedar/cluster`, …), and the test file `tests/test_eda` was split into several files (150 move disagreements). In addition, its test files contain many identical twin warnings (e.g. repeated broad `pytest.raises(Exception)` assertions, `python:S5958`), which SonarQube re-keyed in 95 cases, more than in all other repositories together. Twin swaps do not change any count, only which of two identical warnings is called "the same".
- jsosa/LFPtools (64.8 %) is the same pattern: top-level scripts moved into a `lfptools/` package (211 of 233 disagreements).

The four AI-declared repositories with simpler histories agree at 83–99 %. Because the low-agreement cases are restructurings and the tracker follows them, the disagreement makes Pre-AI introductions *smaller*, not larger, than SonarQube would report.

## 4. Failure cases

| # | Failure case | How it was found | Effect | Resolution |
|---|---|---|---|---|
| FC1 | **Wrong match after code inserted above an issue.** Nearest-line matching paired a finding with a different warning of the same rule when lines shifted (dhSegment `dh_segment/io/PAGE.py`, L652 → L722 matched to L449). | Disagreement with SonarQube in the pilot | False introductions and removals | **Fixed (v1).** Lines mapped through a diff before nearest-line matching, 15-line limit. dhSegment identity agreement 91.6 % → 97.5 %. |
| FC2 | **Generated code counted as source.** dhSegment committed a `build/` copy of its package. | Introduction spike in the pilot | 146 fake issues | **Fixed (v1).** `build/`, `dist/`, `vendor/`, `site-packages/`, `*.egg-info/` and similar folders excluded from findings and LOC in both groups (getavalon/core LOC 48k → 14.5k). |
| FC3 | **Renamed / moved files.** Package renames and module splits (scedar, getavalon, LFPtools). | SonarQube comparison | Without handling, every issue in a moved file is removed and re-introduced | **Fixed (v2).** Rename threshold 40 % plus the "moved" step (section 1). 207 false re-introductions removed (section 2). |
| FC4 | **Identical twin warnings.** Several identical findings in one file. | Identity disagreement analysis | Identities could swap between twins | **Fixed (v2).** Optimal assignment on mapped line distance. Counts were never affected. |
| FC5 | **Edited flagged line.** The flagged line changes, same rule and message. | Identity disagreement analysis | Same issue or a new issue: ambiguous | **Reported.** Matched by message within 15 mapped lines (355 cases). |
| FC6 | **Removal mechanism of multi-line and comment findings.** The "code still present?" check used the comment-stripped code of the whole multi-line block, so a commented-out-code finding (`python:S125`) normalised to an empty string, and multi-line findings were compared as one joined string. | Manual validation (section 5) | Overstated `code_changed` | **Fixed (v2).** Whitespace-only normalisation (comments kept) and a contiguous block check; 30 removals reclassified to `code_still_present` (28 in the combined v2 run). See the note on issue #1891 below. |
| FC7 | **Failed SonarQube analyses.** 7 of 360 analysed commits (2 pilot, 5 main). | Scan log | Gap in the SonarQube series | **Handled.** Commit skipped for SonarQube only; histories bridged across the gap. |
| FC8 | **Sampling gaps.** Sampled commits can be months apart. | Design limitation | Short-lived issues between two sampled commits are never seen; removal is attributed to the next sampled commit | **Reported.** Lifetimes given in analysed commits and in days. |
| FC9 | **Different file coverage of the tools.** Semgrep CE skips test folders by default; SonarQube and Ruff analyse all `.py` files. | Inspection of Semgrep output | Security findings in tests are not counted | **Reported.** Same for both groups. |

## 5. Manual validation of 10 issue histories

Ten histories were sampled from the whole-history data set, stratified by group and outcome (seed 42), and checked against the source at the introduction commit, the last commit where the issue was seen, and the first commit after removal. The sample is in [`results_phaseC/manual_validation_sample.md`](../results_phaseC/manual_validation_sample.md) (with GitHub links). Issue numbers are those of the v1 run; the v2 number is given in brackets.

| Issue | Repository | Rule | Introduction | Persistence | Removal: v1 label → v2 label → check |
|---|---|---|---|---|---|
| #3836 (v2 #3766) | jaxleyverse/jaxley | python:S8510 shadowed loop variable | ✔ L1209 | ✔ | code_changed → code_changed → ✔ line changed |
| #3654 (v2 #3582) | jaxleyverse/jaxley | python:S2638 method signature | ✔ L44 | ✔ | code_changed → code_changed → ✔ signature changed |
| #4647 (v2 #4584) | mit-acl/tcaff | python:S5797 constant condition | ✔ `if False:` L249 | ✔ | file_deleted → file_deleted → ✔ file missing |
| #946 (v2 #913) | binsync/declib | python:S1135 TODO | ✔ L1828 | ✔ L1828 → L2234 | still open → still open ✔ |
| #5271 (v2 #5202) | mit-acl/tcaff | python:S117 naming | ✔ L65 | ✔ | still open → still open ✔ |
| #1891 (v2 #1806) | hanyas/sds | python:S125 commented-out code | ✔ L368 | ✔ L368 → L384 | code_changed → code_changed → ✔ see note |
| #2947 (v2 #2847) | initc3/HoneyBadgerMPC | python:S117 naming | ✔ L207 | ✔ | code_changed → code_changed → ✔ line changed |
| #140 (v2 #136) | TaylorResearchLab/scedar | python:S125 commented-out code | ✔ L549 | v1 ✘ lost at the package split; v2 ✔ followed `scxplit/cluster.py` → `scedar/cluster/mirac.py` | file_deleted → code_changed → ✔ v2 (the commented line is gone from `mirac.py`, which still exists) |
| #3333 (v2 #3235) | initc3/HoneyBadgerMPC | python:S112 generic exception | ✔ L89 | ✔ | still open → still open ✔ |
| #4254 (v2 #4192) | jsosa/LFPtools | python:S6734 `inplace=True` | ✔ L443 | ✔ | still open → still open ✔ |

**Note on #1891 (correction of the October report).** In October this case was reported as a tracker error ("line still present"). On re-checking, the error was in the *checking script*, not in the tracker: the checker stripped comments, so the commented-out line became an empty string, which trivially "matched" an empty line in the new file. Looking at the source directly, the commented-out code was removed, so `code_changed` is correct. The general problem behind it (comment findings and multi-line blocks) was real and is fixed as FC6.

**Result (v2):** introduction correct in 10 of 10; persistence correct in 10 of 10 (v1: 9 of 10, #140 lost at the package split); removal mechanism correct in 6 of 6 removed issues.

## 6. Validation on all 40 pairs

The same checks were run on the full dataset (80 repositories, whole history; `results_ext/validation_*.csv`):

- **Matching:** 66 % exact, 22 % exact twins (optimal assignment), 12 % message, 0.2 % moved.
- **Agreement with SonarQube:** median event agreement 83.4 % (minimum 45.5 %), median identity agreement 82.9 %.
- **Lowest identity agreement:** lgactna/fastlabel (25.9 %). Almost all its disagreements (611 of 622) are identical warnings in generated model code that SonarQube re-keys between analyses (twins, FC4). Its event agreement is 99.1 %, so its introduction and removal counts are not affected. The next lowest (60–62 %: thingless/viewshed, scedar, PCB-Blender) follow the move and twin patterns of section 3.

## 7. Files

| File | Content |
|---|---|
| `results*/validation_sonar_agreement.csv` | Identity agreement per repository |
| `results*/validation_event_agreement.csv` | Event agreement per repository |
| `results*/validation_disagreement_reasons.csv` | Reasons for disagreement per repository |
| `results*/validation_match_methods.csv` | Matches by method, with ambiguous counts |
| `results_phaseC/tracker_fix_impact*.csv` | Effect of each tracker fix (section 2) |
| `data/archives/derived_*.zip` → `match_log.csv` | Every matching decision (method, ambiguity) |
