#!/usr/bin/env bash
# Build the self-contained API executable.
# Run this once; the .NET app will use the exe automatically.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "╔══════════════════════════════════════════╗"
echo "║   DataCleanPro — Build API Executable    ║"
echo "╚══════════════════════════════════════════╝"

VENV_PY="$ROOT/backend/venv/bin/python"

if [ ! -f "$VENV_PY" ]; then
  echo ""
  echo "▶ Setting up Python venv first..."
  cd "$ROOT/backend"
  python3 -m venv venv
  venv/bin/pip install --upgrade pip -q
  venv/bin/pip install -r requirements.txt -q
fi

echo ""
echo "▶ Building exe..."
cd "$ROOT/backend"
"$VENV_PY" build_exe.py

EXE="$ROOT/backend/dist/datacleanpro_api"
if [ -f "$EXE" ]; then
  SIZE=$(du -sh "$EXE" | cut -f1)
  echo ""
  echo "✅ Done!  $EXE  ($SIZE)"
  echo ""
  echo "   Now run ./run.sh to start DataCleanPro using the exe."
fi
