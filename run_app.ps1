# run_app.ps1 - start the Issue Lifelines web app (http://localhost:5000). Stop with Ctrl+C.
$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot
. (Join-Path $Root 'env.ps1')

$py = "$Root\.venv\Scripts\python.exe"
& $py -c "import flask" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Installing Flask into the project's .venv (first run only)..." -ForegroundColor Cyan
  & "$Root\tools\uv\uv.exe" pip install --python $py flask
}
if (-not (Test-Path "$Root\app\study.db")) {
  Write-Host "Building app\study.db ..." -ForegroundColor Cyan
  & $py "$Root\app\database.py"
}
Start-Job -ScriptBlock { Start-Sleep 2; Start-Process "http://localhost:5000" } | Out-Null
Push-Location "$Root\app"
try { & $py app.py } finally { Pop-Location }
