# Rule-to-attribute mappings

Copied from the replication package of Cotroneo, Improta and Varriale, *What is Changing in Software Development? An Open-Source Code Quality Assessment Before and After AI* (Zenodo record 21870905, folder `mappings/`), and used unchanged (only the free-text `notes` column of the SonarQube file is omitted):

| File | Content |
|---|---|
| `sonar_python_rule_attribute_mapping.csv` | SonarQube Python rules → Maintainability / Reliability (rules with several qualities or Security are marked `Excluded`) |
| `ruff_rule_attribute_mapping.csv` | Ruff PERF (perflint) rules → Performance Efficiency |
| `semgrep_pattern_attribute_mapping.csv` | Semgrep security bundles → Security |

How they are applied, and how our observed rules compare with them, is described in [`../docs/ANALYSIS.md`](../docs/ANALYSIS.md), section 2.
