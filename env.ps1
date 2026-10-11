# env.ps1 - puts the portable tools on PATH for THIS PowerShell window only.
# Nothing is changed in Windows. Close the window and it is gone.
#   Use:  . .\env.ps1     (note the dot and space at the start)
$Root  = $PSScriptRoot
$Tools = Join-Path $Root 'tools'

# keep all caches / configs inside the project folder (keeps Windows clean)
$env:UV_CACHE_DIR          = "$Tools\cache\uv"
$env:UV_PYTHON_INSTALL_DIR = "$Tools\python"
$env:UV_TOOL_DIR           = "$Tools\cache\uv-tools"
$env:MPLCONFIGDIR          = "$Tools\cache\matplotlib"
$env:SEMGREP_SETTINGS_FILE = "$Tools\cache\semgrep\settings.yml"
$env:SEMGREP_LOG_FILE      = "$Tools\cache\semgrep\semgrep.log"
$env:SEMGREP_VERSION_CACHE_PATH = "$Tools\cache\semgrep\version"
$env:SEMGREP_ENABLE_VERSION_CHECK = '0'
$env:SEMGREP_SEND_METRICS  = 'off'
$env:XDG_CONFIG_HOME       = "$Tools\cache\xdg"
$env:XDG_CACHE_HOME        = "$Tools\cache\xdg-cache"
$env:PYTHONUTF8            = '1'
$env:PYTHONIOENCODING      = 'utf-8'
$env:GIT_CONFIG_GLOBAL     = "$Root\tools\gitconfig"   # no changes to your personal git config
New-Item -ItemType Directory -Force -Path "$Tools\cache\semgrep","$Tools\cache\matplotlib" | Out-Null
if (-not (Test-Path $env:GIT_CONFIG_GLOBAL)) {
  "[core]`n`tlongpaths = true`n`tautocrlf = false`n[advice]`n`tdetachedHead = false" | Set-Content -Encoding ASCII $env:GIT_CONFIG_GLOBAL
}

$jdkBin = Get-ChildItem "$Tools\jdk" -Filter java.exe -Recurse -ErrorAction SilentlyContinue |
          Where-Object { $_.FullName -like '*\bin\java.exe' } | Select-Object -First 1
if ($jdkBin) {
  $env:JAVA_HOME       = Split-Path (Split-Path $jdkBin.FullName)
  $env:SONAR_JAVA_PATH = $jdkBin.FullName
}
$scBin = Get-ChildItem "$Tools\scanner" -Filter sonar-scanner.bat -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1

$add = @("$Tools\git\cmd", "$Tools\uv", "$Root\.venv\Scripts", "$Root\.venv-semgrep\Scripts")
if ($env:JAVA_HOME) { $add += "$env:JAVA_HOME\bin" }
if ($scBin)         { $add += $scBin.DirectoryName }
$env:PATH = ($add -join ';') + ';' + $env:PATH

Write-Host "ai_study tools active in this window." -ForegroundColor Green
