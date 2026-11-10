#!/bin/bash
# run_app.sh - start the Issue Lifelines web app on http://localhost:5000 (stop with Ctrl+C). macOS / Linux.
set -e
cd "$(dirname "$0")"
PY=.venv/bin/python; [ -x $PY ] || { echo "Run ./setup_mac.sh first."; exit 1; }
if [ -f app/study.db.xz ] && { [ ! -f app/study.db ] || [ app/study.db.xz -nt app/study.db ]; }; then
  echo "Unpacking app/study.db ..."
  $PY -c "import lzma,shutil,sys; shutil.copyfileobj(lzma.open(sys.argv[1]), open(sys.argv[2],'wb'))" app/study.db.xz app/study.db
fi
[ -f app/study.db ] || $PY app/database.py
( sleep 3; open http://localhost:5000 2>/dev/null || xdg-open http://localhost:5000 2>/dev/null || true ) &
cd app && exec ../$PY app.py
