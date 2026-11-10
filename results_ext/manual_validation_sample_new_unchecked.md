# Manual validation sample (10 issue histories, seed 42)

## Issue 6127 - AI - Dynatrace-Dave-Mauney/Automation
- Tool/rule: sonarqube `python:S125` (maintainability)
- Message: Remove this commented out code.
- Introduced: 640aadc489 (2022-12-08); seen in snapshots 2-11; lines 124 > 125 > 126
- Paths: Reporting/report_settings20_web_application_details.py
- Removal: b5c9344abc -> code_changed
- [code at introduction](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/640aadc489069bda949fedc6cb860382f0147837/Reporting/report_settings20_web_application_details.py#L124) | [code last seen](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/25daee3ed192fb5eee709af139e34177bcce902e/Reporting/report_settings20_web_application_details.py#L126) | [removal commit diff](https://github.com/Dynatrace-Dave-Mauney/Automation/commit/b5c9344abc93ed90ceb4eb2e551df75d225f9007)

## Issue 34303 - AI - internetarchive/iari
- Tool/rule: sonarqube `python:S5709` (maintainability)
- Message: Derive this class from "Exception" instead of "BaseException".
- Introduced: 2373a6a9ac (2022-11-25); seen in snapshots 13-27; lines 29 > 37 > 33 > 5 > 9
- Paths: src/models/exceptions.py
- Removal: 120f17f41b -> code_changed
- [code at introduction](https://github.com/internetarchive/iari/blob/2373a6a9acad3283dd5494e12394cf8f987744e0/src/models/exceptions.py#L29) | [code last seen](https://github.com/internetarchive/iari/blob/aa10f83318de1456177d355dcf77bab4b0484318/src/models/exceptions.py#L9) | [removal commit diff](https://github.com/internetarchive/iari/commit/120f17f41b73484abb4058c17ef785a6176715ed)

## Issue 11730 - AI - FennisRobert/EMerge
- Tool/rule: sonarqube `python:S117` (maintainability)
- Message: Rename this local variable "Exg" to match the regular expression ^[_a-z][a-z0-9_]*$.
- Introduced: 754a5c0ca1 (2025-07-15); seen in snapshots 6-23; lines 668 > 669 > 684 > 691 > 723 > 775 > 773 > 794 > 822 > 842 > 875 > 894 > 994 > 1014 > 1028 > 1029 > 1032
- Paths: src/_emerge/physics/microwave/microwave_bc.py > src/emerge/_emerge/physics/microwave/microwave_bc.py
- Removal: dd5149014d -> file_deleted
- [code at introduction](https://github.com/FennisRobert/EMerge/blob/754a5c0ca1531c2e59dd7eb590596664a0f92ec0/src/_emerge/physics/microwave/microwave_bc.py#L668) | [code last seen](https://github.com/FennisRobert/EMerge/blob/7b269c904dc61d5fe103512bade76e2453422ca4/src/emerge/_emerge/physics/microwave/microwave_bc.py#L1032) | [removal commit diff](https://github.com/FennisRobert/EMerge/commit/dd5149014d556607083082cf4f75ba14696dcfc0)

## Issue 7449 - AI - Dynatrace-Dave-Mauney/Automation
- Tool/rule: sonarqube `python:S3776` (maintainability)
- Message: Refactor this function to reduce its Cognitive Complexity from 18 to the 15 allowed.
- Introduced: 91f62e52aa (2024-01-26); seen in snapshots 18-30; lines 735 > 296 > 308
- Paths: Reporting/ManagementZones/report_management_zone_coverage.py > Dashboards/generate_management_zone_specific_dashboards.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/91f62e52aa465f3a70b3ec88bd0020eabdec9b59/Reporting/ManagementZones/report_management_zone_coverage.py#L735) | [code last seen](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/b3d5e737914730f22535439463c939e08f4d5fea/Dashboards/generate_management_zone_specific_dashboards.py#L308)

## Issue 22757 - AI - binsync/declib
- Tool/rule: sonarqube `python:S1135` (maintainability)
- Message: Complete the task associated to this "TODO" comment.
- Introduced: 644c7bb92f (2024-10-01); seen in snapshots 16-30; lines 649 > 650 > 655 > 669 > 697 > 722 > 725 > 762
- Paths: libbs/decompilers/ida/compat.py > declib/decompilers/ida/compat.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/binsync/declib/blob/644c7bb92f4ea10c9de772c88427c2e21c01e4fb/libbs/decompilers/ida/compat.py#L649) | [code last seen](https://github.com/binsync/declib/blob/cd38076e65d8f36d83430a1bfbb0e494b58ceeed/declib/decompilers/ida/compat.py#L762)

## Issue 25731 - PreAI - drepetto/chiplotle
- Tool/rule: sonarqube `python:S2245` (security)
- Message: Make sure that using this pseudorandom number generator is safe here.
- Introduced: 6dff81d4ae (2011-02-20); seen in snapshots 25-28; lines 35
- Paths: chiplotle/geometry/factory/arrow.py > chiplotle/geometry/shapes/arrow.py
- Removal: 68adefe6f9 -> code_changed
- [code at introduction](https://github.com/drepetto/chiplotle/blob/6dff81d4ae3702861a181edc7eb1e1d692bd2cd7/chiplotle/geometry/factory/arrow.py#L35) | [code last seen](https://github.com/drepetto/chiplotle/blob/065ba3bddd437e1cea118bf7b2a632bc4929528f/chiplotle/geometry/shapes/arrow.py#L35) | [removal commit diff](https://github.com/drepetto/chiplotle/commit/68adefe6f98e6c4e598ca630f742ebdc67c1fabf)

## Issue 19297 - PreAI - ToniRV/Kimera-VIO-Evaluation
- Tool/rule: sonarqube `python:S1192` (maintainability)
- Message: Define a constant instead of duplicating this literal "\033[99m" 8 times.
- Introduced: d510004f6f (2018-12-03); seen in snapshots 3-7; lines 162 > 163
- Paths: src/main_evaluation.py > evaluation/main_evaluation.py
- Removal: 2447d92c01 -> code_changed
- [code at introduction](https://github.com/ToniRV/Kimera-VIO-Evaluation/blob/d510004f6f7adb389b1d2e81a23feb784c1f9718/src/main_evaluation.py#L162) | [code last seen](https://github.com/ToniRV/Kimera-VIO-Evaluation/blob/002ff7f61f49034c1219d5d9ecb6f264ff9100ed/evaluation/main_evaluation.py#L163) | [removal commit diff](https://github.com/ToniRV/Kimera-VIO-Evaluation/commit/2447d92c0168f9229fc8ed5eb348a2171508d137)

## Issue 53819 - PreAI - spcl/stencilflow
- Tool/rule: sonarqube `python:S7498` (maintainability)
- Message: Replace this constructor call with a literal.
- Introduced: 7cc5a00940 (2018-10-10); seen in snapshots 2-9; lines 35 > 36
- Paths: StencilChainSimulator/code/parser.py
- Removal: d4f56e19ee -> file_deleted
- [code at introduction](https://github.com/spcl/stencilflow/blob/7cc5a00940c2e183e65e5a02bb1a022b47a6adca/StencilChainSimulator/code/parser.py#L35) | [code last seen](https://github.com/spcl/stencilflow/blob/7f6cf531eae9fc6ab0c9f2b10fe48fa70bd086e3/StencilChainSimulator/code/parser.py#L36) | [removal commit diff](https://github.com/spcl/stencilflow/commit/d4f56e19ee0596da3c6de1f29e00f70d4a7a9a97)

## Issue 55000 - PreAI - tdseher/addtag-project
- Tool/rule: sonarqube `python:S1172` (maintainability)
- Message: Remove the unused function parameter "seq".
- Introduced: 287af65f65 (2018-07-11); seen in snapshots 9-30; lines 374
- Paths: source/oligos/addtagprimer.py > source/thermodynamics/addtagprimer.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/tdseher/addtag-project/blob/287af65f65289e8b843779d83534547e65c0e592/source/oligos/addtagprimer.py#L374) | [code last seen](https://github.com/tdseher/addtag-project/blob/eecb7277a5b546e23a08a341e30ac67adb88f90b/source/thermodynamics/addtagprimer.py#L374)

## Issue 26952 - PreAI - ekraka/SSnet
- Tool/rule: sonarqube `python:S117` (maintainability)
- Message: Rename this parameter "M" to match the regular expression ^[_a-z][a-z0-9_]*$.
- Introduced: dff5fd68d7 (2019-12-11); seen in snapshots 2-30; lines 327
- Paths: SSnet_ECF/tool.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/ekraka/SSnet/blob/dff5fd68d7615425869d1476636b6c35ae5d7ded/SSnet_ECF/tool.py#L327) | [code last seen](https://github.com/ekraka/SSnet/blob/6a28140b2e54e5415553609a612fcae92f9103f0/SSnet_ECF/tool.py#L327)

