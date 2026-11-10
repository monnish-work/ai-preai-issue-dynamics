# Manual validation sample (10 issue histories, seed 42)

## Issue 2379 - AI - jaxleyverse/jaxley
- Tool/rule: sonarqube `python:S107` (maintainability)
- Message: Function "step_voltage_explicit" has 20 parameters, which is greater than the 13 authorized.
- Introduced: 82cce2d598 (2024-09-13); seen in snapshots 2-2; lines 16
- Paths: jaxley/solver_voltage.py
- Removal: ecfe7e8f47 -> code_changed
- [code at introduction](https://github.com/jaxleyverse/jaxley/blob/82cce2d59865992084650a99cbb354c5e42d2c4d/jaxley/solver_voltage.py#L16) | [code last seen](https://github.com/jaxleyverse/jaxley/blob/82cce2d59865992084650a99cbb354c5e42d2c4d/jaxley/solver_voltage.py#L16) | [removal commit diff](https://github.com/jaxleyverse/jaxley/commit/ecfe7e8f47287989dc108081ca06837a6ec7334c)

## Issue 2392 - AI - jaxleyverse/jaxley
- Tool/rule: sonarqube `python:S1172` (maintainability)
- Message: Remove the unused function parameter "root_inds".
- Introduced: 82cce2d598 (2024-09-13); seen in snapshots 2-2; lines 221
- Paths: jaxley/solver_voltage.py
- Removal: ecfe7e8f47 -> code_changed
- [code at introduction](https://github.com/jaxleyverse/jaxley/blob/82cce2d59865992084650a99cbb354c5e42d2c4d/jaxley/solver_voltage.py#L221) | [code last seen](https://github.com/jaxleyverse/jaxley/blob/82cce2d59865992084650a99cbb354c5e42d2c4d/jaxley/solver_voltage.py#L221) | [removal commit diff](https://github.com/jaxleyverse/jaxley/commit/ecfe7e8f47287989dc108081ca06837a6ec7334c)

## Issue 3216 - AI - mit-acl/tcaff
- Tool/rule: sonarqube `python:S1481` (maintainability)
- Message: Remove the unused local variable "Tij_gt".
- Introduced: ffad80604c (2024-04-13); seen in snapshots 9-9; lines 333
- Paths: demo/motlee_runner.py
- Removal: d60178b22d -> file_deleted
- [code at introduction](https://github.com/mit-acl/tcaff/blob/ffad80604c94f4536ba1f81139bf7951c3007a72/demo/motlee_runner.py#L333) | [code last seen](https://github.com/mit-acl/tcaff/blob/ffad80604c94f4536ba1f81139bf7951c3007a72/demo/motlee_runner.py#L333) | [removal commit diff](https://github.com/mit-acl/tcaff/commit/d60178b22da1c187fad7b64f383ae89fe60d0186)

## Issue 3164 - AI - mit-acl/tcaff
- Tool/rule: sonarqube `python:S5890` (maintainability)
- Message: Replace the type hint "float" with "Optional[float]" or don't assign "None" to "height"
- Introduced: b137309dc4 (2024-01-29); seen in snapshots 3-14; lines 41 > 55 > 84 > 87
- Paths: motlee/realign/object_map.py > tcaff/realign/object_map.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/mit-acl/tcaff/blob/b137309dc40a075315ad5978b77a4dc561428151/motlee/realign/object_map.py#L41) | [code last seen](https://github.com/mit-acl/tcaff/blob/e181c9143ddb105c6aa3c36ebcabf592c26d058b/tcaff/realign/object_map.py#L87)

## Issue 863 - AI - binsync/declib
- Tool/rule: sonarqube `python:S7632` (maintainability)
- Message: Fix the syntax of this issue suppression comment.
- Introduced: e91535126f (2026-08-02); seen in snapshots 7-8; lines 2622 > 2911
- Paths: declib/cli/decompiler_cli.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/binsync/declib/blob/e91535126f86e7dccf41fc607bd9037857b6d881/declib/cli/decompiler_cli.py#L2622) | [code last seen](https://github.com/binsync/declib/blob/cd38076e65d8f36d83430a1bfbb0e494b58ceeed/declib/cli/decompiler_cli.py#L2911)

## Issue 1027 - PreAI - getavalon/core
- Tool/rule: sonarqube `python:S1172` (maintainability)
- Message: Remove the unused function parameter "root".
- Introduced: 97719c8724 (2017-06-27); seen in snapshots 2-4; lines 206 > 208
- Paths: avalon/tools/cbloader/app.py
- Removal: ae625eb3e0 -> code_changed
- [code at introduction](https://github.com/getavalon/core/blob/97719c8724a8b84c822434ee0ffa595d21b2099a/avalon/tools/cbloader/app.py#L206) | [code last seen](https://github.com/getavalon/core/blob/a1a0e3856e50263dcc7cd85b8906b87393d79d05/avalon/tools/cbloader/app.py#L208) | [removal commit diff](https://github.com/getavalon/core/commit/ae625eb3e0f040de391214d0ae7ee004c904e5d4)

## Issue 128 - PreAI - TaylorResearchLab/scedar
- Tool/rule: sonarqube `python:S8495` (maintainability)
- Message: Refactor this function to always return tuples of the same length.
- Introduced: ed678b440a (2018-03-23); seen in snapshots 5-13; lines 389 > 434 > 435 > 252
- Paths: scxplit/cluster.py > scedar/cluster.py > scedar/cluster/mdl.py
- Removal: ff6ffced27 -> code_changed
- [code at introduction](https://github.com/TaylorResearchLab/scedar/blob/ed678b440a0b89a57c393cce9b877092e229613b/scxplit/cluster.py#L389) | [code last seen](https://github.com/TaylorResearchLab/scedar/blob/8d43174cd47bc9a93aed07b36d38e7e9766b19c9/scedar/cluster/mdl.py#L252) | [removal commit diff](https://github.com/TaylorResearchLab/scedar/commit/ff6ffced27d321b2bf7ef301499a34f30cd86a34)

## Issue 176 - PreAI - TaylorResearchLab/scedar
- Tool/rule: sonarqube `python:S5778` (maintainability)
- Message: Refactor this exception test to have only one invocation possibly throwing an exception.
- Introduced: cdd7d07cbc (2018-03-27); seen in snapshots 9-13; lines 55
- Paths: tests/test_cluster/test_hct.py
- Removal: ff6ffced27 -> file_deleted
- [code at introduction](https://github.com/TaylorResearchLab/scedar/blob/cdd7d07cbc85b7d7bfb78e4fdc4b3cc0ffe875fd/tests/test_cluster/test_hct.py#L55) | [code last seen](https://github.com/TaylorResearchLab/scedar/blob/8d43174cd47bc9a93aed07b36d38e7e9766b19c9/tests/test_cluster/test_hct.py#L55) | [removal commit diff](https://github.com/TaylorResearchLab/scedar/commit/ff6ffced27d321b2bf7ef301499a34f30cd86a34)

## Issue 1148 - PreAI - getavalon/core
- Tool/rule: sonarqube `python:S7498` (maintainability)
- Message: Replace this constructor call with a literal.
- Introduced: ae625eb3e0 (2019-08-03); seen in snapshots 5-8; lines 230 > 223
- Paths: avalon/tools/cbsceneinventory/app.py > avalon/tools/sceneinventory/app.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/getavalon/core/blob/ae625eb3e0f040de391214d0ae7ee004c904e5d4/avalon/tools/cbsceneinventory/app.py#L230) | [code last seen](https://github.com/getavalon/core/blob/91f5ae87120f61d8beb57af099d321e28178399f/avalon/tools/sceneinventory/app.py#L223)

## Issue 2202 - PreAI - initc3/HoneyBadgerMPC
- Tool/rule: sonarqube `python:S7497` (reliability)
- Message: Ensure that the asyncio.CancelledError exception is re-raised after your cleanup code.
- Introduced: 1800f7c51c (2019-06-05); seen in snapshots 5-10; lines 174 > 205 > 207
- Paths: honeybadgermpc/batch_reconstruction.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/initc3/HoneyBadgerMPC/blob/1800f7c51c0aab5f567f35e89037912c4893e86b/honeybadgermpc/batch_reconstruction.py#L174) | [code last seen](https://github.com/initc3/HoneyBadgerMPC/blob/f2a9ac58547bba2d4ed7d2f1a99a8aa97ef35b44/honeybadgermpc/batch_reconstruction.py#L207)

