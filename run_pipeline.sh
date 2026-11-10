#!/bin/bash
# run_pipeline.sh - reproduce every result from the archived raw scan output (macOS / Linux).
#   1. unpacks data/archives (raw scans of all 80 repositories + pilot)
#   2. clones the analysed repositories into repos/ (the tracker reads the code at each analysed commit)
#   3. AI-declaration windows, tracking (whole history + windows), validation, analysis + sensitivity runs,
#      process metrics, docs/RESULTS.md and the web-app database
# Takes about 30-60 minutes; needs about 6 GB of disk for the clones.
set -e
cd "$(dirname "$0")"
PY=.venv/bin/python; [ -x $PY ] || { echo "Run ./setup_mac.sh first."; exit 1; }
export MPLCONFIGDIR="$PWD/tools/cache/matplotlib"; mkdir -p "$MPLCONFIGDIR"
echo "==> unpacking archives"; $PY scripts/unpack_archives.py
echo "==> cloning repositories"
for f in data/study_repos_phaseC.csv data/study_repos_phaseD.csv data/study_repos_phaseE1.csv data/study_repos_phaseE2.csv data/study_repos.csv; do
  tail -n +2 "$f" | $PY -c "import csv,sys; [print(r[1]) for r in csv.reader(sys.stdin)]"
done | sort -u | while read r; do d="repos/${r/\//__}"; [ -d "$d" ] || git clone -q "https://github.com/$r.git" "$d" || echo "clone failed: $r"; done
echo "==> windows and combined data set"
$PY scripts/declaration_windows.py data/raw_phaseC data/raw_phaseD data/raw_phaseE
rm -rf data/raw_ext; mkdir -p data/raw_ext
for d in data/raw_phaseC/*/ data/raw_phaseD/*/ data/raw_phaseE/*/; do t=${d%/}; ln -s "../${t#data/}" "data/raw_ext/$(basename "$d")"; done
echo "==> tracking (4 runs in parallel)"
$PY scripts/track.py phaseC > /dev/null &
$PY scripts/track.py ext > /dev/null &
OUT_TAG=_paired WINDOW_FILE=data/paired_windows.csv $PY scripts/track.py phaseC > /dev/null &
OUT_TAG=_paired WINDOW_FILE=data/paired_windows.csv $PY scripts/track.py ext > /dev/null &
wait
for t in ext_paired ext phaseC_paired phaseC; do
  echo "==> $t: validation, analysis, sensitivity runs, process metrics"
  $PY scripts/validate.py $t > /dev/null
  $PY scripts/analyze.py $t > /dev/null 2>&1 || true
  $PY scripts/analyze_v2.py $t > /dev/null
  MAPPING=strict SUBDIR=v2_sens_strict_mapping $PY scripts/analyze_v2.py $t > /dev/null
  LOC=py_loc SUBDIR=v2_sens_nonblank_loc $PY scripts/analyze_v2.py $t > /dev/null
  TIERS=S SUBDIR=v2_sens_strict_tier $PY scripts/analyze_v2.py $t > /dev/null
  $PY scripts/process_metrics.py $t > /dev/null
done
$PY scripts/make_report.py ext_paired ext
$PY app/database.py
echo "==> Finished. Results: docs/RESULTS.md, results_ext*/ ; web app: ./run_app.sh"
