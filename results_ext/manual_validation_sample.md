# Manual validation sample (10 issue histories, seed 42)

## Issue 6347 - AI - mit-acl/tcaff
- Tool/rule: sonarqube `python:S7498` (maintainability)
- Message: Replace this constructor call with a literal.
- Introduced: bf3aa4c8a0 (2023-07-06); seen in snapshots 8-17; lines 32 > 29 > 22
- Paths: motlee/realign/frame_align_filter.py
- Removal: 77dd439249 -> code_changed
- [code at introduction](https://github.com/mit-acl/tcaff/blob/bf3aa4c8a0f5b2b5594a7c3aff8ee436799f20b9/motlee/realign/frame_align_filter.py#L32) | [code last seen](https://github.com/mit-acl/tcaff/blob/40b748e3364e8865a34bfde8889676dac534ee06/motlee/realign/frame_align_filter.py#L22) | [removal commit diff](https://github.com/mit-acl/tcaff/commit/77dd439249d1cda7f1af25953dc81e983915185e)

## Issue 4832 - AI - jaxleyverse/jaxley
- Tool/rule: sonarqube `python:S5797` (maintainability)
- Message: Replace this expression; used as a condition it will always be constant.
- Introduced: a73745371f (2023-05-10); seen in snapshots 4-6; lines 181 > 248 > 280
- Paths: neurax/solver_voltage.py
- Removal: f91f7b277d -> code_changed
- [code at introduction](https://github.com/jaxleyverse/jaxley/blob/a73745371f32fe7733c12ccd539820d66b236663/neurax/solver_voltage.py#L181) | [code last seen](https://github.com/jaxleyverse/jaxley/blob/1221a2311f4a9cae1f7528bd1a9fd763c9f1cd7a/neurax/solver_voltage.py#L280) | [removal commit diff](https://github.com/jaxleyverse/jaxley/commit/f91f7b277d1ecac2f9a7b3f459d89bb747e77015)

## Issue 1501 - AI - asdf1434/noise-schedule-exp
- Tool/rule: sonarqube `python:S3776` (maintainability)
- Message: Refactor this function to reduce its Cognitive Complexity from 30 to the 15 allowed.
- Introduced: 28c677bd33 (2026-09-10); seen in snapshots 19-27; lines 85
- Paths: scripts/plots/plot_shift_fid.py
- Removal: 56e9339eda -> file_deleted
- [code at introduction](https://github.com/asdf1434/noise-schedule-exp/blob/28c677bd333d0510b9051fdf6404814f097ff6c9/scripts/plots/plot_shift_fid.py#L85) | [code last seen](https://github.com/asdf1434/noise-schedule-exp/blob/b8909e25c484cb1c86edefcfb70b989766be995d/scripts/plots/plot_shift_fid.py#L85) | [removal commit diff](https://github.com/asdf1434/noise-schedule-exp/commit/56e9339edaa1111d6823b603736b5388d327f828)

## Issue 6551 - AI - mit-acl/tcaff
- Tool/rule: sonarqube `python:S117` (maintainability)
- Message: Rename this parameter "K" to match the regular expression ^[_a-z][a-z0-9_]*$.
- Introduced: 40b748e336 (2024-01-15); seen in snapshots 17-30; lines 86
- Paths: motlee/utils/cam_utils.py > tcaff/utils/cam_utils.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/mit-acl/tcaff/blob/40b748e3364e8865a34bfde8889676dac534ee06/motlee/utils/cam_utils.py#L86) | [code last seen](https://github.com/mit-acl/tcaff/blob/e181c9143ddb105c6aa3c36ebcabf592c26d058b/tcaff/utils/cam_utils.py#L86)

## Issue 6524 - AI - mit-acl/tcaff
- Tool/rule: sonarqube `python:S1763` (reliability)
- Message: Delete this unreachable code or refactor the code to make it reachable.
- Introduced: 1db62fef1a (2024-01-05); seen in snapshots 16-30; lines 125 > 135 > 139 > 134
- Paths: motlee/tcaff/tcaff.py > tcaff/tcaff/tcaff.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/mit-acl/tcaff/blob/1db62fef1a384d706ad0fcfd360a22689b928d89/motlee/tcaff/tcaff.py#L125) | [code last seen](https://github.com/mit-acl/tcaff/blob/e181c9143ddb105c6aa3c36ebcabf592c26d058b/tcaff/tcaff/tcaff.py#L134)

## Issue 7501 - PreAI - predict-idlab/seriesdistancematrix
- Tool/rule: sonarqube `python:S6730` (maintainability)
- Message: Replace this deprecated "numpy" type alias with the builtin type "int".
- Introduced: c6921be878 (2019-01-09); seen in snapshots 14-27; lines 28
- Paths: distancematrix/consumer/threshold_counter.py
- Removal: 13ad8032f0 -> code_changed
- [code at introduction](https://github.com/predict-idlab/seriesdistancematrix/blob/c6921be87815b8e38fddbdf0fa7e9943da4f1156/distancematrix/consumer/threshold_counter.py#L28) | [code last seen](https://github.com/predict-idlab/seriesdistancematrix/blob/4a35709e0f4f6c101d9e3f5cf608d9a4a693063a/distancematrix/consumer/threshold_counter.py#L28) | [removal commit diff](https://github.com/predict-idlab/seriesdistancematrix/commit/13ad8032f0be2124e2f6a4e94e30a46732bd22e5)

## Issue 1146 - PreAI - ToniRV/Kimera-VIO-Evaluation
- Tool/rule: sonarqube `python:S112` (maintainability)
- Message: Replace this generic exception class with a more specific one.
- Introduced: d510004f6f (2018-12-03); seen in snapshots 3-7; lines 198 > 199
- Paths: src/main_evaluation.py > evaluation/main_evaluation.py
- Removal: 2447d92c01 -> code_changed
- [code at introduction](https://github.com/ToniRV/Kimera-VIO-Evaluation/blob/d510004f6f7adb389b1d2e81a23feb784c1f9718/src/main_evaluation.py#L198) | [code last seen](https://github.com/ToniRV/Kimera-VIO-Evaluation/blob/002ff7f61f49034c1219d5d9ecb6f264ff9100ed/evaluation/main_evaluation.py#L199) | [removal commit diff](https://github.com/ToniRV/Kimera-VIO-Evaluation/commit/2447d92c0168f9229fc8ed5eb348a2171508d137)

## Issue 685 - PreAI - TaylorResearchLab/scedar
- Tool/rule: sonarqube `python:S5958` (maintainability)
- Message: This assertion is too broad; use a more specific exception type or check the exception message.
- Introduced: 04d7c2c3ae (2018-03-20); seen in snapshots 3-8; lines 263 > 264 > 293 > 325 > 424
- Paths: tests/test_eda.py
- Removal: cdd7d07cbc -> file_deleted
- [code at introduction](https://github.com/TaylorResearchLab/scedar/blob/04d7c2c3ae4e1a66989653c96897337e68d60abe/tests/test_eda.py#L263) | [code last seen](https://github.com/TaylorResearchLab/scedar/blob/3fea3f46b2b63dc637852509e50685bb1e026e8b/tests/test_eda.py#L424) | [removal commit diff](https://github.com/TaylorResearchLab/scedar/commit/cdd7d07cbc85b7d7bfb78e4fdc4b3cc0ffe875fd)

## Issue 5524 - PreAI - jsosa/LFPtools
- Tool/rule: sonarqube `python:S6729` (maintainability)
- Message: Use "np.nonzero" when only the condition parameter is provided to "np.where".
- Introduced: 36d74a5799 (2018-01-16); seen in snapshots 3-30; lines 72 > 71
- Paths: misc_utils.py > lfptools/misc_utils.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/jsosa/LFPtools/blob/36d74a57995761098344c0954a74884ef6427858/misc_utils.py#L72) | [code last seen](https://github.com/jsosa/LFPtools/blob/34fbbd86fd712498af45f74b96076ad287ea728e/lfptools/misc_utils.py#L71)

## Issue 824 - PreAI - TaylorResearchLab/scedar
- Tool/rule: sonarqube `python:S5958` (maintainability)
- Message: This assertion is too broad; use a more specific exception type or check the exception message.
- Introduced: cdd7d07cbc (2018-03-27); seen in snapshots 9-30; lines 96 > 110 > 117 > 121 > 122
- Paths: tests/test_eda/test_sdm.py > tests/test_eda/test_dense_sdm.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/TaylorResearchLab/scedar/blob/cdd7d07cbc85b7d7bfb78e4fdc4b3cc0ffe875fd/tests/test_eda/test_sdm.py#L96) | [code last seen](https://github.com/TaylorResearchLab/scedar/blob/f8cd7dab9f885a0c58d127a9ee3b143d7e4bae06/tests/test_eda/test_dense_sdm.py#L122)

