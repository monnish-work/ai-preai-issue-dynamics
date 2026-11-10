# Manual validation sample (10 issue histories, seed 42)

## Issue 4406 - AI - mit-acl/tcaff
- Tool/rule: semgrep `python.lang.security.deserialization.pickle.avoid-pickle` (security)
- Message: Avoid using `pickle`, which is known to lead to code execution vulnerabilities. When unpickling, the serialized data cou
- Introduced: 047749aaf2 (2024-02-08); seen in snapshots 5-10; lines 116 > 122 > 126 > 133 > 71
- Paths: demo/motlee_runner.py > demo/demo.py
- Removal: 707a204ad1 -> code_changed
- [code at introduction](https://github.com/mit-acl/tcaff/blob/047749aaf26ad8a137aaf13213c94d22ac2bc857/demo/motlee_runner.py#L116) | [code last seen](https://github.com/mit-acl/tcaff/blob/d60178b22da1c187fad7b64f383ae89fe60d0186/demo/demo.py#L71) | [removal commit diff](https://github.com/mit-acl/tcaff/commit/707a204ad1df1420eff596424941325fdc7e29e9)

## Issue 417 - AI - Quent-DL/MasterThesis_ElectroLoc
- Tool/rule: sonarqube `python:S1481` (maintainability)
- Message: Remove the unused local variable "old_contacts".
- Introduced: a1214d1dd9 (2025-04-04); seen in snapshots 6-6; lines 81
- Paths: ElectrodesLocalization/src/main.py
- Removal: fd6f88c20d -> code_changed
- [code at introduction](https://github.com/Quent-DL/MasterThesis_ElectroLoc/blob/a1214d1dd95f7b0a6841910da1f818558afdca01/ElectrodesLocalization/src/main.py#L81) | [code last seen](https://github.com/Quent-DL/MasterThesis_ElectroLoc/blob/a1214d1dd95f7b0a6841910da1f818558afdca01/ElectrodesLocalization/src/main.py#L81) | [removal commit diff](https://github.com/Quent-DL/MasterThesis_ElectroLoc/commit/fd6f88c20d3f635fd3ef88b2f190deee9a5bf706)

## Issue 4450 - AI - mit-acl/tcaff
- Tool/rule: sonarqube `python:S117` (maintainability)
- Message: Rename this local variable "T_w_ri" to match the regular expression ^[_a-z][a-z0-9_]*$.
- Introduced: ffad80604c (2024-04-13); seen in snapshots 9-9; lines 387
- Paths: demo/motlee_runner.py
- Removal: d60178b22d -> file_deleted
- [code at introduction](https://github.com/mit-acl/tcaff/blob/ffad80604c94f4536ba1f81139bf7951c3007a72/demo/motlee_runner.py#L387) | [code last seen](https://github.com/mit-acl/tcaff/blob/ffad80604c94f4536ba1f81139bf7951c3007a72/demo/motlee_runner.py#L387) | [removal commit diff](https://github.com/mit-acl/tcaff/commit/d60178b22da1c187fad7b64f383ae89fe60d0186)

## Issue 191 - AI - AdityaSavara/jsongrapher-py
- Tool/rule: sonarqube `python:S1172` (maintainability)
- Message: Remove the unused function parameter "input_data".
- Introduced: 39785c422b (2025-05-28); seen in snapshots 9-16; lines 49
- Paths: examples/example_11_local_python_calls/Langmuir_isotherm_kadskdes.py > tutorials/tutorial_11_local_python_calls/Langmuir_isotherm_kadskdes.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/AdityaSavara/jsongrapher-py/blob/39785c422b4c9c4cff2fb50af01c527246a8e1d7/examples/example_11_local_python_calls/Langmuir_isotherm_kadskdes.py#L49) | [code last seen](https://github.com/AdityaSavara/jsongrapher-py/blob/e9b26e368d9768bb2a7793c22af7250f4e31f51d/tutorials/tutorial_11_local_python_calls/Langmuir_isotherm_kadskdes.py#L49)

## Issue 3602 - AI - jaxleyverse/jaxley
- Tool/rule: sonarqube `python:S1854` (maintainability)
- Message: Remove this assignment to local variable 'sink_comp_inds'; the value is never used.
- Introduced: 61675ec0ba (2026-09-03); seen in snapshots 10-10; lines 458
- Paths: jaxley/solver_voltage.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/jaxleyverse/jaxley/blob/61675ec0bae860be87dd18c7699c9f3e9767e9b2/jaxley/solver_voltage.py#L458) | [code last seen](https://github.com/jaxleyverse/jaxley/blob/61675ec0bae860be87dd18c7699c9f3e9767e9b2/jaxley/solver_voltage.py#L458)

## Issue 610 - PreAI - TaylorResearchLab/scedar
- Tool/rule: sonarqube `python:S1940` (maintainability)
- Message: Use the opposite operator ("!=") instead.
- Introduced: 09f1f14c11 (2018-03-19); seen in snapshots 2-13; lines 79 > 67 > 70 > 80 > 85
- Paths: scxplit/utils.py > scedar/utils.py
- Removal: ff6ffced27 -> code_changed
- [code at introduction](https://github.com/TaylorResearchLab/scedar/blob/09f1f14c112823be64c36fcc178c4c90f655691b/scxplit/utils.py#L79) | [code last seen](https://github.com/TaylorResearchLab/scedar/blob/8d43174cd47bc9a93aed07b36d38e7e9766b19c9/scedar/utils.py#L85) | [removal commit diff](https://github.com/TaylorResearchLab/scedar/commit/ff6ffced27d321b2bf7ef301499a34f30cd86a34)

## Issue 2426 - PreAI - hanyas/sds
- Tool/rule: sonarqube `python:S6711` (maintainability)
- Message: Use a "numpy.random.Generator" here instead of this legacy function.
- Introduced: 7b4f34f0a9 (2020-04-30); seen in snapshots 2-4; lines 55
- Paths: sds/utils.py
- Removal: 3c195fb9cb -> code_changed
- [code at introduction](https://github.com/hanyas/sds/blob/7b4f34f0a9492c28860a738c400fe023dbe87511/sds/utils.py#L55) | [code last seen](https://github.com/hanyas/sds/blob/4af366b621d93f85fd1ce1dd6ff3fdecf9f65b37/sds/utils.py#L55) | [removal commit diff](https://github.com/hanyas/sds/commit/3c195fb9cbd88a9284287d62c0eacb6afc4598a7)

## Issue 1001 - PreAI - TaylorResearchLab/scedar
- Tool/rule: sonarqube `python:S1172` (maintainability)
- Message: Remove the unused function parameter "transform_queue_size".
- Introduced: 5ce9227e02 (2018-07-20); seen in snapshots 22-23; lines 461
- Paths: scedar/eda/sdm.py
- Removal: c81c632b74 -> code_still_present
- [code at introduction](https://github.com/TaylorResearchLab/scedar/blob/5ce9227e02996c2c60cab0342d8ebccf3dddc2c0/scedar/eda/sdm.py#L461) | [code last seen](https://github.com/TaylorResearchLab/scedar/blob/d58bc3564fc78e28f86800b6d16f60d0ee544eb0/scedar/eda/sdm.py#L461) | [removal commit diff](https://github.com/TaylorResearchLab/scedar/commit/c81c632b74de41543054517015b4774bd775e7d8)

## Issue 2128 - PreAI - getavalon/core
- Tool/rule: sonarqube `python:S5806` (maintainability)
- Message: Rename this variable; it shadows a builtin.
- Introduced: ae625eb3e0 (2019-08-03); seen in snapshots 5-8; lines 36 > 39
- Paths: avalon/tools/cbloader/widgets.py > avalon/tools/loader/widgets.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/getavalon/core/blob/ae625eb3e0f040de391214d0ae7ee004c904e5d4/avalon/tools/cbloader/widgets.py#L36) | [code last seen](https://github.com/getavalon/core/blob/91f5ae87120f61d8beb57af099d321e28178399f/avalon/tools/loader/widgets.py#L39)

## Issue 2131 - PreAI - getavalon/core
- Tool/rule: sonarqube `python:S5806` (maintainability)
- Message: Rename this variable; it shadows a builtin.
- Introduced: ae625eb3e0 (2019-08-03); seen in snapshots 5-8; lines 272 > 273 > 320
- Paths: avalon/tools/cbloader/widgets.py > avalon/tools/loader/widgets.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/getavalon/core/blob/ae625eb3e0f040de391214d0ae7ee004c904e5d4/avalon/tools/cbloader/widgets.py#L272) | [code last seen](https://github.com/getavalon/core/blob/91f5ae87120f61d8beb57af099d321e28178399f/avalon/tools/loader/widgets.py#L320)

