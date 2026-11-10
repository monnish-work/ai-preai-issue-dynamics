# run_wide_search.ps1 - wider GitHub search for AI-declared repositories (dataset extension).
# Asks for a GitHub token and keeps it in memory for this window only: it is never written to a file.
# Create the token at https://github.com/settings/tokens (classic, no scopes needed, or fine-grained read-only
# public access) and DELETE it on GitHub when the search is finished.
# Takes 2-6 hours (GitHub allows 10 code searches per minute). Safe to stop and re-run: finished queries are cached.
$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot
. (Join-Path $Root 'env.ps1')
$py = (Get-ChildItem "$Root\tools\python" -Recurse -Filter python.exe -ErrorAction SilentlyContinue |
       Where-Object { $_.FullName -notlike "*venv*" } | Select-Object -First 1).FullName
$env:PYTHONPATH = "$Root\.venv\Lib\site-packages"   # Smart App Control blocks .venv\Scripts\python.exe
$sec = Read-Host "Paste the GitHub token (input is hidden)" -AsSecureString
$env:GITHUB_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
try { & $py "$Root\scripts\find_candidates_wide.py" @args }
finally { Remove-Item Env:\GITHUB_TOKEN -ErrorAction SilentlyContinue }
Write-Host "Results: data\candidates\wide\ai_candidates_wide.csv" -ForegroundColor Green
