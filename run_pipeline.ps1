# run_pipeline.ps1 - re-run tracking (v2), validation and analysis for every data set, then rebuild the app database.
# Needs the raw scan output in data\raw and data\raw_phaseC (unzip data\archives\raw_*.zip) and the repositories
# cloned in repos\ (done by scan_repos.py). Ruff output (ruff.json) is already included in data\raw_phaseC;
# to recreate it, install Ruff 0.17.4 and run:  python scripts\run_ruff.py phaseC
$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot
. (Join-Path $Root 'env.ps1')
$py = (Get-ChildItem "$Root\tools\python" -Recurse -Filter python.exe -ErrorAction SilentlyContinue |
       Where-Object { $_.FullName -notlike "*venv*" } | Select-Object -First 1).FullName
$env:PYTHONPATH = "$Root\.venv\Lib\site-packages"   # Smart App Control blocks .venv\Scripts\python.exe
Set-Location $Root

Write-Host "`n==> Ruff, AI-declaration windows, combined data set (data\raw_ext = raw_phaseC + raw_phaseD + raw_phaseE)" -ForegroundColor Cyan
& $py scripts\declaration_windows.py data\raw_phaseC data\raw_phaseD data\raw_phaseE
New-Item -ItemType Directory -Force data\raw_ext | Out-Null
foreach ($d in (Get-ChildItem data\raw_phaseC, data\raw_phaseD, data\raw_phaseE -Directory)) {
  if (-not (Test-Path "data\raw_ext\$($d.Name)")) { Copy-Item $d.FullName "data\raw_ext\$($d.Name)" -Recurse } }
Write-Host "`n==> tracking: first 5 pairs and all pairs, whole history and AI-declaration windows" -ForegroundColor Cyan
& $py scripts\track.py phaseC
& $py scripts\track.py ext
$env:OUT_TAG = '_paired'; $env:WINDOW_FILE = 'data\paired_windows.csv'
& $py scripts\track.py phaseC
& $py scripts\track.py ext
Remove-Item Env:\OUT_TAG, Env:\WINDOW_FILE -ErrorAction SilentlyContinue

foreach ($t in @('ext_paired', 'ext', 'phaseC_paired', 'phaseC')) {
  Write-Host "`n==> $t : validation, analysis (v2 + sensitivity), process metrics" -ForegroundColor Cyan
  & $py scripts\validate.py $t
  & $py scripts\analyze.py $t
  & $py scripts\analyze_v2.py $t
  $env:MAPPING = 'strict'; $env:SUBDIR = 'v2_sens_strict_mapping'; & $py scripts\analyze_v2.py $t
  Remove-Item Env:\MAPPING; $env:LOC = 'py_loc'; $env:SUBDIR = 'v2_sens_nonblank_loc'; & $py scripts\analyze_v2.py $t
  Remove-Item Env:\LOC; $env:TIERS = 'S'; $env:SUBDIR = 'v2_sens_strict_tier'; & $py scripts\analyze_v2.py $t
  Remove-Item Env:\TIERS, Env:\SUBDIR
  & $py scripts\process_metrics.py $t
}
& $py scripts\make_report.py ext_paired ext
Write-Host "`n==> building app\study.db" -ForegroundColor Cyan
& $py app\database.py
Write-Host "`nPipeline finished. Start the app with .\run_app.ps1" -ForegroundColor Green
