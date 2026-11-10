# run_app.ps1 - start the Issue Lifelines web app (http://localhost:5000). Stop with Ctrl+C.
# Uses the main Python interpreter in tools\python together with the packages in .venv,
# because Windows Smart App Control can block the small python.exe launcher inside .venv.
$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot
. (Join-Path $Root 'env.ps1')

$py = (Get-ChildItem "$Root\tools\python" -Recurse -Filter python.exe -ErrorAction SilentlyContinue |
       Where-Object { $_.FullName -notlike "*venv*" } | Select-Object -First 1).FullName
if (-not $py) { Write-Host "Python not found in tools\python - run setup.ps1 first." -ForegroundColor Red; exit 1 }
$env:PYTHONPATH = "$Root\.venv\Lib\site-packages"

& $py -c "import flask" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Installing Flask into the project's .venv (first run only)..." -ForegroundColor Cyan
  & "$Root\tools\uv\uv.exe" pip install --python "$Root\.venv\Scripts\python.exe" flask
}
$xz = "$Root\app\study.db.xz"; $db = "$Root\app\study.db"
if ((Test-Path $xz) -and ((-not (Test-Path $db)) -or ((Get-Item $xz).LastWriteTime -gt (Get-Item $db).LastWriteTime))) {
  Write-Host "Unpacking app\study.db ..." -ForegroundColor Cyan
  & $py -c "import lzma,shutil,sys; shutil.copyfileobj(lzma.open(sys.argv[1]), open(sys.argv[2],'wb'))" "$Root\app\study.db.xz" "$Root\app\study.db"
}
if (-not (Test-Path "$Root\app\study.db")) {
  Write-Host "Building app\study.db ..." -ForegroundColor Cyan
  & $py "$Root\app\database.py"
}
Start-Job -ScriptBlock { Start-Sleep 3; Start-Process "http://localhost:5000" } | Out-Null
Push-Location "$Root\app"
try { & $py app.py } finally { Pop-Location }
