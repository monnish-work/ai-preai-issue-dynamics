# Manual validation sample (10 issue histories, seed 42)

## Issue 3836 - AI - jaxleyverse/jaxley
- Tool/rule: sonarqube `python:S8510` (maintainability)
- Message: Rename this loop variable; it shadows the outer loop variable "i".
- Introduced: 240a1616cb (2025-04-22); seen in snapshots 27-27; lines 1209
- Paths: jaxley/io/graph.py
- Removal: d85905c72b -> code_changed
- [code at introduction](https://github.com/jaxleyverse/jaxley/blob/240a1616cb6ea660a99a00f4f6755407485af897/jaxley/io/graph.py#L1209) | [code last seen](https://github.com/jaxleyverse/jaxley/blob/240a1616cb6ea660a99a00f4f6755407485af897/jaxley/io/graph.py#L1209) | [removal commit diff](https://github.com/jaxleyverse/jaxley/commit/d85905c72b616515b52695cda54ed1c8f162501d)

## Issue 3654 - AI - jaxleyverse/jaxley
- Tool/rule: sonarqube `python:S2638` (maintainability)
- Message: Remove parameter post_voltage or provide default value.
- Introduced: c0b5ca1228 (2024-03-26); seen in snapshots 19-19; lines 44
- Paths: jaxley/synapses/ionotropic.py
- Removal: 8957d1e424 -> code_changed
- [code at introduction](https://github.com/jaxleyverse/jaxley/blob/c0b5ca122854eb188ef931d843cb7c299a0c88f9/jaxley/synapses/ionotropic.py#L44) | [code last seen](https://github.com/jaxleyverse/jaxley/blob/c0b5ca122854eb188ef931d843cb7c299a0c88f9/jaxley/synapses/ionotropic.py#L44) | [removal commit diff](https://github.com/jaxleyverse/jaxley/commit/8957d1e424916af76d77e7323d4c80e56a27935e)

## Issue 4647 - AI - mit-acl/tcaff
- Tool/rule: sonarqube `python:S5797` (maintainability)
- Message: Replace this expression; used as a condition it will always be constant.
- Introduced: 5df2289fe5 (2023-05-26); seen in snapshots 4-7; lines 249 > 248
- Paths: motlee/realign/frame_realigner.py
- Removal: bf3aa4c8a0 -> file_deleted
- [code at introduction](https://github.com/mit-acl/tcaff/blob/5df2289fe5330c11a67e84128b4dd4c71c42e67d/motlee/realign/frame_realigner.py#L249) | [code last seen](https://github.com/mit-acl/tcaff/blob/217a6d94f43ce8fab14f6b36486324efebe23382/motlee/realign/frame_realigner.py#L248) | [removal commit diff](https://github.com/mit-acl/tcaff/commit/bf3aa4c8a0f5b2b5594a7c3aff8ee436799f20b9)

## Issue 946 - AI - binsync/declib
- Tool/rule: sonarqube `python:S1135` (maintainability)
- Message: Complete the task associated to this "TODO" comment.
- Introduced: 0ce5c351cc (2025-08-30); seen in snapshots 22-30; lines 1828 > 1824 > 1931 > 2145 > 2206 > 2234
- Paths: libbs/decompilers/ida/compat.py > declib/decompilers/ida/compat.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/binsync/declib/blob/0ce5c351cc81c1a0120f763aeba584fdb9dc2820/libbs/decompilers/ida/compat.py#L1828) | [code last seen](https://github.com/binsync/declib/blob/cd38076e65d8f36d83430a1bfbb0e494b58ceeed/declib/decompilers/ida/compat.py#L2234)

## Issue 5271 - AI - mit-acl/tcaff
- Tool/rule: sonarqube `python:S117` (maintainability)
- Message: Rename this local variable "scaledEigenvalue1" to match the regular expression ^[_a-z][a-z0-9_]*$.
- Introduced: 707a204ad1 (2024-10-02); seen in snapshots 27-30; lines 65
- Paths: tcaff/fastsam3D/utils.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/mit-acl/tcaff/blob/707a204ad1df1420eff596424941325fdc7e29e9/tcaff/fastsam3D/utils.py#L65) | [code last seen](https://github.com/mit-acl/tcaff/blob/e181c9143ddb105c6aa3c36ebcabf592c26d058b/tcaff/fastsam3D/utils.py#L65)

## Issue 1891 - PreAI - hanyas/sds
- Tool/rule: sonarqube `python:S125` (maintainability)
- Message: Remove this commented out code.
- Introduced: 9bfed29791 (2019-10-02); seen in snapshots 12-13; lines 368 > 384
- Paths: sds/transitions.py
- Removal: a3163a234d -> code_changed
- [code at introduction](https://github.com/hanyas/sds/blob/9bfed29791aa856cb939e0e33242138f975cd9fd/sds/transitions.py#L368) | [code last seen](https://github.com/hanyas/sds/blob/0757c47cd6d4f4511b1f0a679a4b0c7852085b24/sds/transitions.py#L384) | [removal commit diff](https://github.com/hanyas/sds/commit/a3163a234dedfccdfc109e25cb2bc1e6192e2c0f)

## Issue 2947 - PreAI - initc3/HoneyBadgerMPC
- Tool/rule: sonarqube `python:S117` (maintainability)
- Message: Rename this local variable "Poly" to match the regular expression ^[_a-z][a-z0-9_]*$.
- Introduced: ac99903146 (2019-01-24); seen in snapshots 7-10; lines 207 > 214 > 232 > 234
- Paths: honeybadgermpc/batch_reconstruction.py
- Removal: 9dbf1649a1 -> code_changed
- [code at introduction](https://github.com/initc3/HoneyBadgerMPC/blob/ac99903146080aba37ce42753eef09047f25888c/honeybadgermpc/batch_reconstruction.py#L207) | [code last seen](https://github.com/initc3/HoneyBadgerMPC/blob/558e6547870e9499fe362a7916e7ba12099dad85/honeybadgermpc/batch_reconstruction.py#L234) | [removal commit diff](https://github.com/initc3/HoneyBadgerMPC/commit/9dbf1649a1fd2795f8ee86de05459c4cca4719aa)

## Issue 140 - PreAI - TaylorResearchLab/scedar
- Tool/rule: sonarqube `python:S125` (maintainability)
- Message: Remove this commented out code.
- Introduced: ed678b440a (2018-03-23); seen in snapshots 5-8; lines 549 > 599 > 600 > 650
- Paths: scxplit/cluster.py > scedar/cluster.py
- Removal: cdd7d07cbc -> file_deleted
- [code at introduction](https://github.com/TaylorResearchLab/scedar/blob/ed678b440a0b89a57c393cce9b877092e229613b/scxplit/cluster.py#L549) | [code last seen](https://github.com/TaylorResearchLab/scedar/blob/3fea3f46b2b63dc637852509e50685bb1e026e8b/scedar/cluster.py#L650) | [removal commit diff](https://github.com/TaylorResearchLab/scedar/commit/cdd7d07cbc85b7d7bfb78e4fdc4b3cc0ffe875fd)

## Issue 3333 - PreAI - initc3/HoneyBadgerMPC
- Tool/rule: sonarqube `python:S112` (maintainability)
- Message: Replace this generic exception class with a more specific one.
- Introduced: f307970cb1 (2019-04-19); seen in snapshots 19-30; lines 89 > 79 > 80 > 93 > 94 > 90 > 92 > 95
- Paths: progs/jubjub.py > honeybadgermpc/progs/jubjub.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/initc3/HoneyBadgerMPC/blob/f307970cb19bcb35082dd84b0c5758e1a7982c29/progs/jubjub.py#L89) | [code last seen](https://github.com/initc3/HoneyBadgerMPC/blob/f2a9ac58547bba2d4ed7d2f1a99a8aa97ef35b44/honeybadgermpc/progs/jubjub.py#L95)

## Issue 4254 - PreAI - jsosa/LFPtools
- Tool/rule: sonarqube `python:S6734` (maintainability)
- Message: Do not use "inplace=True" when modifying a dataframe.
- Introduced: a01ec45061 (2018-02-28); seen in snapshots 6-30; lines 443 > 450 > 480 > 501 > 495
- Paths: lfptools/prepdata.py
- Removal: - -> still open (censored)
- [code at introduction](https://github.com/jsosa/LFPtools/blob/a01ec45061b1bb4b7b0ed1fb1c82345a4c1dde08/lfptools/prepdata.py#L443) | [code last seen](https://github.com/jsosa/LFPtools/blob/34fbbd86fd712498af45f74b96076ad287ea728e/lfptools/prepdata.py#L495)

