# start-sonar.ps1 - starts the local SonarQube server (keep this window open).
# Then open http://localhost:9000 in your browser (first login admin / admin).
# Stop it by pressing Ctrl+C in this window.
. (Join-Path $PSScriptRoot 'env.ps1')
$bat = Get-ChildItem "$PSScriptRoot\tools\sonarqube" -Filter StartSonar.bat -Recurse |
       Where-Object { $_.FullName -like '*windows-x86-64*' } | Select-Object -First 1
if (-not $bat) { throw "SonarQube not found - run setup.ps1 first." }
Write-Host "Starting SonarQube (takes 1-3 minutes)... open http://localhost:9000 when you see 'SonarQube is operational'" -ForegroundColor Cyan
& $bat.FullName
