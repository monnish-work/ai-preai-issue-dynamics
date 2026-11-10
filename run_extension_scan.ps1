# run_extension_scan.ps1 - scans the 16 new matched pairs (M6-M22, without M8) of the dataset extension.
# One command, unattended:   .\run_extension_scan.ps1
# - starts SonarQube (a second window opens: keep it open),
# - clones the 34 repositories into repos\ and scans 30 commits each with SonarQube + Semgrep,
#   smallest pairs first, so that every finished pair is complete even if you stop early,
# - keeps the laptop awake while it runs (only while this window is open; no Windows setting is changed),
# - safe to stop (Ctrl+C) and start again: finished commits are skipped,
# - at the end packs the raw output into data\raw_phaseD.zip.
# Expected time: about 6-8 hours for all 960 commits (about 22 s per commit).
param([string]$List = 'data\study_repos_phaseD.csv', [string]$Out = 'data\raw_phaseD')
$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot
. (Join-Path $Root 'env.ps1')
Set-Location $Root
$py = (Get-ChildItem "$Root\tools\python" -Recurse -Filter python.exe -ErrorAction SilentlyContinue |
       Where-Object { $_.FullName -notlike "*venv*" } | Select-Object -First 1).FullName
if (-not $py) { Write-Host "Python not found in tools\python - run setup.ps1 first." -ForegroundColor Red; exit 1 }
$env:PYTHONPATH = "$Root\.venv\Lib\site-packages"   # Smart App Control can block .venv\Scripts\*.exe

# Semgrep: Windows blocks the semgrep.exe launcher (Smart App Control), so Semgrep is started from Python directly,
# with the packages of .venv-semgrep (site.addsitedir also loads pywin32, which Semgrep needs on Windows).
$sp = "$Root\.venv-semgrep\Lib\site-packages"
$code = "import sys,site; sys.path=[p for p in sys.path if '.venv\\Lib' not in p]; site.addsitedir(r'$sp'); from semgrep.console_scripts.pysemgrep import main; sys.argv=['pysemgrep']+sys.argv[1:]; sys.exit(main())"
$env:SEMGREP_CMD = "$py|-c|$code"
& $py -c $code --version
if ($LASTEXITCODE -ne 0) { Write-Host "WARNING: Semgrep cannot run; security findings will be missing." -ForegroundColor Yellow }

# keep the computer awake while this script runs (released automatically when the window closes)
Add-Type -Namespace Win32 -Name Power -MemberDefinition '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint f);'
[Win32.Power]::SetThreadExecutionState([uint32]2147483649) | Out-Null   # ES_CONTINUOUS | ES_SYSTEM_REQUIRED

# fresh SonarQube projects (a first attempt without Semgrep already created projects with later analysis dates)
$env:SONAR_KEY_SUFFIX = '_r2'
$t0 = Get-Date
& $py scripts\scan_repos.py --repos $List --mode spread --n 30 --out $Out
[Win32.Power]::SetThreadExecutionState([uint32]2147483648) | Out-Null

Write-Host "`nScan of $List finished." -ForegroundColor Green
