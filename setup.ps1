# =====================================================================
#  setup.ps1  -  Portable, self-contained toolkit for the AI vs PreAI study
#  Everything is downloaded INTO this folder. Nothing is installed in
#  Windows, no admin rights, no PATH/registry changes.
#  To remove everything later: run cleanup.ps1 (or just delete the folder).
#
#  Run with:
#     powershell -ExecutionPolicy Bypass -File .\setup.ps1
# =====================================================================
$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'   # makes downloads much faster
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Root  = $PSScriptRoot
$Tools = Join-Path $Root 'tools'
$Dl    = Join-Path $Root 'downloads'
New-Item -ItemType Directory -Force -Path $Tools, $Dl | Out-Null

# ---- pinned versions (recorded for reproducibility) ------------------
$V = @{
  MinGit      = '2.55.0.5'
  MinGitTag   = 'v2.55.0.windows.5'
  Python      = '3.12'
  Semgrep     = '1.178.0'
  SonarQube   = @('26.8.0.126808','26.7.0.124771')   # tried in order
  Scanner     = @('8.1.0.6389','8.0.1.6346')          # tried in order
}

function Say($msg)  { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Ok($msg)   { Write-Host "    OK  $msg" -ForegroundColor Green }

function Get-File($url, $out) {
  if (Test-Path $out) { Ok "already downloaded: $(Split-Path $out -Leaf)"; return $true }
  try {
    Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing
    Ok "downloaded $(Split-Path $out -Leaf)"; return $true
  } catch {
    if (Test-Path $out) { Remove-Item $out -Force }
    Write-Host "    could not download $url" -ForegroundColor Yellow
    return $false
  }
}

function Unzip($zip, $dest) {
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  tar -xf $zip -C $dest          # built into Windows 10/11, much faster than Expand-Archive
}

# Keep every cache/config of the tools INSIDE this folder
. (Join-Path $Root 'env.ps1')

# ---------------------------------------------------------------------
Say "1/6  Git (portable MinGit)"
if (-not (Test-Path "$Tools\git\cmd\git.exe")) {
  $z = "$Dl\MinGit.zip"
  Get-File "https://github.com/git-for-windows/git/releases/download/$($V.MinGitTag)/MinGit-$($V.MinGit)-64-bit.zip" $z | Out-Null
  Unzip $z "$Tools\git"
}
& "$Tools\git\cmd\git.exe" --version

# ---------------------------------------------------------------------
Say "2/6  uv (portable Python manager)"
if (-not (Test-Path "$Tools\uv\uv.exe")) {
  $z = "$Dl\uv.zip"
  Get-File "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip" $z | Out-Null
  Unzip $z "$Tools\uv"
}
& "$Tools\uv\uv.exe" --version

# ---------------------------------------------------------------------
Say "3/6  Python $($V.Python) + analysis libraries (in .venv)"
if (-not (Test-Path "$Root\.venv\Scripts\python.exe")) {
  & "$Tools\uv\uv.exe" venv --python $V.Python "$Root\.venv"
}
& "$Tools\uv\uv.exe" pip install --python "$Root\.venv\Scripts\python.exe" `
    pandas matplotlib scipy lifelines requests openpyxl
& "$Root\.venv\Scripts\python.exe" --version

# ---------------------------------------------------------------------
Say "4/6  Semgrep Community Edition $($V.Semgrep) (separate .venv-semgrep)"
if (-not (Test-Path "$Root\.venv-semgrep\Scripts\python.exe")) {
  & "$Tools\uv\uv.exe" venv --python $V.Python "$Root\.venv-semgrep"
}
& "$Tools\uv\uv.exe" pip install --python "$Root\.venv-semgrep\Scripts\python.exe" "semgrep==$($V.Semgrep)"
& "$Root\.venv-semgrep\Scripts\semgrep.exe" --version

# ---------------------------------------------------------------------
Say "5/6  Java 21 (portable Temurin JDK, needed by SonarQube)"
if (-not (Get-ChildItem "$Tools\jdk" -Filter java.exe -Recurse -ErrorAction SilentlyContinue)) {
  $z = "$Dl\jdk21.zip"
  Get-File "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse" $z | Out-Null
  Unzip $z "$Tools\jdk"
}
$java = (Get-ChildItem "$Tools\jdk" -Filter java.exe -Recurse | Where-Object { $_.FullName -like '*\bin\java.exe' } | Select-Object -First 1).FullName
Ok "Java at $java"

# ---------------------------------------------------------------------
Say "6/6  SonarQube Community Build + SonarScanner CLI"
if (-not (Get-ChildItem "$Tools\sonarqube" -Filter StartSonar.bat -Recurse -ErrorAction SilentlyContinue)) {
  $got = $false
  foreach ($ver in $V.SonarQube) {
    $z = "$Dl\sonarqube-$ver.zip"
    if (Get-File "https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-$ver.zip" $z) {
      Unzip $z "$Tools\sonarqube"; $got = $true; break
    }
  }
  if (-not $got) { throw "Could not download SonarQube - check your internet connection and try again." }
}
if (-not (Get-ChildItem "$Tools\scanner" -Filter sonar-scanner.bat -Recurse -ErrorAction SilentlyContinue)) {
  $got = $false
  foreach ($ver in $V.Scanner) {
    $z = "$Dl\sonar-scanner-$ver.zip"
    if (Get-File "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$ver-windows-x64.zip" $z) {
      Unzip $z "$Tools\scanner"; $got = $true; break
    }
  }
  if (-not $got) { throw "Could not download SonarScanner - check your internet connection and try again." }
}
$sq = (Get-ChildItem "$Tools\sonarqube" -Directory | Select-Object -First 1).Name
$sc = (Get-ChildItem "$Tools\scanner"   -Directory | Select-Object -First 1).Name
Ok "SonarQube: $sq"
Ok "Scanner:   $sc"

# ---------------------------------------------------------------------
Say "Recording exact tool versions -> tool_versions.txt"
$ErrorActionPreference = 'Continue'   # java prints its version on stderr
$lines = @(
  "Recorded: $(Get-Date -Format s)",
  "Windows: $([Environment]::OSVersion.VersionString)",
  "Git: $(& "$Tools\git\cmd\git.exe" --version)",
  "uv: $(& "$Tools\uv\uv.exe" --version)",
  "Python: $(& "$Root\.venv\Scripts\python.exe" --version)",
  "Semgrep: $(& "$Root\.venv-semgrep\Scripts\semgrep.exe" --version)",
  "Java: $((& $java -version 2>&1 | Select-Object -First 1).ToString())",
  "SonarQube: $sq",
  "SonarScanner: $sc",
  "Python packages:"
) + (& "$Tools\uv\uv.exe" pip freeze --python "$Root\.venv\Scripts\python.exe")
$lines | Set-Content -Encoding UTF8 "$Root\tool_versions.txt"

# free space: the zip files are no longer needed
Remove-Item $Dl -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`nALL DONE. Setup finished successfully." -ForegroundColor Green
Write-Host "Folder size:" ("{0:N2} GB" -f ((Get-ChildItem $Root -Recurse -File | Measure-Object Length -Sum).Sum / 1GB))
