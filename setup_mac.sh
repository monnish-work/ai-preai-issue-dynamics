#!/bin/bash
# setup_mac.sh - set up the project on macOS (or Linux). Everything stays inside this folder (.venv, tools/).
#   ./setup_mac.sh                  Python environment for the analysis and the web app (needed for everything)
#   ./setup_mac.sh --with-scanners  also Semgrep, Ruff, SonarQube and SonarScanner (only needed to re-scan repositories)
# Needs: python3 (3.11 or 3.12; e.g. `brew install python@3.12`) and git (`xcode-select --install`).
# For --with-scanners also Java 21 (`brew install openjdk@21`).
set -e
cd "$(dirname "$0")"
PY=${PYTHON:-$(command -v python3.12 || command -v python3)}
echo "==> Python: $($PY --version)"
[ -d .venv ] || $PY -m venv .venv
.venv/bin/python -m pip install --upgrade pip -q
.venv/bin/python -m pip install -r requirements.txt
if [ "$1" == "--with-scanners" ]; then
  .venv/bin/python -m pip install -r requirements-scanners.txt
  mkdir -p tools downloads
  SQ=26.8.0.126808; SC=8.1.0.6389
  case "$(uname -s)-$(uname -m)" in
    Darwin-arm64) SCP=macosx-aarch64 ;; Darwin-*) SCP=macosx-x64 ;; *) SCP=linux-x64 ;;
  esac
  [ -f downloads/sonarqube.zip ] || curl -fL -o downloads/sonarqube.zip "https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-$SQ.zip"
  [ -d tools/sonarqube ] || (mkdir -p tools/sonarqube && unzip -q downloads/sonarqube.zip -d tools/sonarqube)
  [ -f downloads/scanner.zip ] || curl -fL -o downloads/scanner.zip "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SC-$SCP.zip"
  [ -d tools/scanner ] || (mkdir -p tools/scanner && unzip -q downloads/scanner.zip -d tools/scanner)
  echo "==> Java: $(java -version 2>&1 | head -1)   (SonarQube needs Java 21)"
fi
{ echo "Recorded: $(date -u +%Y-%m-%dT%H:%M:%S) (macOS/Linux setup)"; echo "OS: $(uname -sm)"; echo "Git: $(git --version)";
  echo "Python: $(.venv/bin/python --version)"; .venv/bin/python -m pip freeze; } > tool_versions_local.txt
echo "==> Done. Start the web app with ./run_app.sh ; reproduce the analysis with ./run_pipeline.sh"
