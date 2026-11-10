# Summary of the November update (version 3)

Status of the points raised on 13 October and 9 November. Full details: [RESULTS.md](RESULTS.md) (all tables, generated from the result files), [ANALYSIS.md](ANALYSIS.md) (definitions and methods), [DATASET.md](DATASET.md) (selection), [TRACKER_VALIDATION.md](TRACKER_VALIDATION.md).

## What was done

| Point | Status |
|---|---|
| Dataset towards 83 pairs | **40 + 40 pairs analysed.** 25 pairs meet the original strict rule (≥ 60 commits, ≥ 2 % declared files); 15 were added with relaxed rules (30–59 commits, or < 2 % declared files) and are marked. Every candidate of the first search was reviewed by hand (79 decisions with reasons in `data/ai_extension_review.csv`). Going beyond 40 needs a wider GitHub search (script ready, [FEASIBILITY.md](FEASIBILITY.md)). |
| Tracker fixes (renames, repeated warnings, multi-line) | Done and measured; median agreement with SonarQube's own tracking on all 80 repositories: 83 % (event), 83 % (identity). |
| Repository-level comparison as main result, multiple-comparison correction | Done: exact Mann–Whitney, Cliff's δ, Holm over 40 tests per window. |
| Lifetime, censoring, baseline issues, removal counts | Defined in ANALYSIS.md §1; counts reconciled in RESULTS.md §8. |
| AI observation window aligned with documented AI use | Done: from the first commit that adds an AI declaration; Pre-AI partner over the same sampled positions. 34 pairs have at least 5 analysed commits in that window (main result); all 40 pairs in the whole-history analysis. |
| "AI-declared", four ISO/IEC 25010 attributes, replication-package mapping and tools, Ruff, density per KLOC, process metrics | Done (ANALYSIS.md §2). |

## Main findings (40 pairs)

1. **AI-declared repositories introduce fewer issues per KLOC and have a lower issue density** than their matched Pre-AI repositories. This holds in both windows, in 29 of 40 pairs (introductions) and 30 of 40 pairs (density). The effect is medium (Cliff's δ ≈ −0.33 to −0.43; e.g. whole history 40.4 vs 82.9 introductions per KLOC).
2. **After Holm correction the evidence is moderate, not conclusive.** 3 of the 40 whole-history tests (all maintainability density and introduction rates) remain significant; in the AI-declaration windows the smallest corrected p-value is 0.06. In the sensitivity runs, 6 whole-history tests survive with the replication-package mapping, and 4 (AI windows) and 6 (whole history) with non-blank lines as KLOC. Restricted to the 25 strict-rule pairs the direction and effect size are the same (e.g. 48.5 vs 80.0 introductions per KLOC) but no test survives correction.
3. **Issue survival differs, but its direction depends on the window** (pooled, supporting evidence only). In the AI-declaration windows issues in AI-declared repositories survive longer (Kaplan–Meier median not reached vs 15 analysed commits). Over the whole history they are removed sooner (17 vs 23). The repository-level median lifetime does not differ (p = 0.47 and 0.89).
4. **Removal mechanism:** after the first AI declaration, AI-declared repositories remove more issues by changing the flagged code (56 % vs 43 %) and fewer by deleting files (33 % vs 47 %). In the 5-pair sample, file deletion had dominated in AI-declared repositories; with 40 pairs that pattern does not hold.
5. **Process metrics differ strongly:** AI-declared repositories have less experienced developers (median 167 vs 356 days since an author's first commit; Holm p < 0.001) and more commits per month (15 vs 7). Part of this is structural: AI-declared projects are younger. This is a likely confounder for finding 1 and is reported, not corrected for.
6. **Security** findings are still rare (122 vs 92 introduced in the AI windows), so RQ3 has low power.

## Points to discuss

1. Are the relaxed-rule pairs acceptable, or should the main result use the 25 strict pairs only (results for both are reported)?
2. Should process metrics (project age, developer experience, activity) be used as covariates in a follow-up model, given finding 5?
3. Is it worth running the wider search to go beyond 40 pairs before 22 November?

## Data-collection notes

- All 2,100 new analysed commits were scanned with the frozen tool versions; SonarQube failed on 21 of them (1 %), and the tracker bridges those gaps.
- Three repositories needed technical workarounds on Windows (file names Windows cannot create, Git LFS). One Pre-AI partner (haxkor/forkever) had to be replaced (DATASET.md §7).
- Pairs M9, M12, M19, M34, M38 and M41 have fewer than 5 analysed commits after the first AI declaration and are used in the whole-history analysis only.
