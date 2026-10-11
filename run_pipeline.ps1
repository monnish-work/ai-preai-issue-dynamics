# run_pipeline.ps1 - re-run tracking, validation and analysis for both data sets, then rebuild the app database.
# Needs the raw scan output in data\raw and data\raw_phaseC, and the repositories cloned in repos\ (done by scan_repos.py).
$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot
. (Join-Path $Root 'env.ps1')
$py = "$Root\.venv\Scripts\python.exe"
Set-Location $Root

foreach ($phase in @('', 'phaseC')) {
  $label = if ($phase) { $phase } else { 'pilot' }
  Write-Host "`n==> $label : tracking issues" -ForegroundColor Cyan
  if ($phase) { & $py scripts\track.py $phase } else { & $py scripts\track.py }
  Write-Host "==> $label : validating tracker" -ForegroundColor Cyan
  if ($phase) { & $py scripts\validate.py $phase } else { & $py scripts\validate.py }
  Write-Host "==> $label : analysis + figures" -ForegroundColor Cyan
  if ($phase) { & $py scripts\analyze.py $phase } else { & $py scripts\analyze.py }
}
Write-Host "`n==> building app\study.db" -ForegroundColor Cyan
& $py app\database.py
Write-Host "`nPipeline finished. Start the app with .\run_app.ps1" -ForegroundColor Green
