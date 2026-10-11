# cleanup.ps1 - removes EVERYTHING this project put on the laptop.
# !! Copy your results/report somewhere else first !!
#   Run from a PowerShell window that is NOT inside the ai_study folder:
#   powershell -ExecutionPolicy Bypass -File $HOME\ai_study\cleanup.ps1
$Root = $PSScriptRoot
$ans = Read-Host "This deletes $Root and everything in it. Type YES to continue"
if ($ans -ne 'YES') { Write-Host "Cancelled."; exit }

# stop SonarQube / Java processes started from this folder
Get-Process java -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "$Root*" } | Stop-Process -Force

# safety net: these would only exist if a tool ignored our settings
foreach ($p in "$HOME\.semgrep", "$env:LOCALAPPDATA\uv") {
  if (Test-Path $p) { Remove-Item $p -Recurse -Force -ErrorAction SilentlyContinue; Write-Host "removed $p" }
}
Set-Location $HOME
Remove-Item $Root -Recurse -Force
Write-Host "Done. Your laptop is back to how it was." -ForegroundColor Green
