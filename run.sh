#!/usr/bin/env bash
# DataCleanPro — start the full application.
# 
# Launch order for the API engine:
#   1. frontend/api/datacleanpro_api   (bundled exe — preferred)
#   2. backend/dist/datacleanpro_api   (dev build output)
#   3. backend/venv/bin/python         (Python venv fallback)
#
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "╔══════════════════════════════════════════╗"
echo "║       DataCleanPro  v1.0                 ║"
echo "╚══════════════════════════════════════════╝"

EXE="$ROOT/backend/dist/datacleanpro_api"
VENV_PY="$ROOT/backend/venv/bin/python"

# ── If no exe and no venv, set up venv as fallback ──────────────────────────
if [ ! -f "$EXE" ] && [ ! -f "$VENV_PY" ]; then
  echo ""
  echo "▶ No exe found — setting up Python venv as fallback..."
  cd "$ROOT/backend"
  python3 -m venv venv
  venv/bin/pip install --upgrade pip -q
  venv/bin/pip install -r requirements.txt -q
  echo "  ✓ Venv ready  (run 'python build_exe.py' in backend/ to build the exe)"
fi

if [ -f "$EXE" ]; then
  echo ""
  echo "  ▸ API engine : $EXE  [exe mode]"
else
  echo ""
  echo "  ▸ API engine : Python venv  [fallback mode]"
  echo "    Tip: cd backend && python build_exe.py  to build a standalone exe"
fi

# Fix #K: track browser-open PID and kill it if the app exits early
BROWSER_PID=""
cleanup() { [ -n "$BROWSER_PID" ] && kill "$BROWSER_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

(sleep 3 && \
  if command -v xdg-open &>/dev/null; then xdg-open http://localhost:5000
  elif command -v open &>/dev/null; then open http://localhost:5000
  fi) &
BROWSER_PID=$!

echo ""
echo "▶ Starting DataCleanPro on http://localhost:5000"
echo "  Press Ctrl+C to stop everything."
echo ""

cd "$ROOT/frontend"
ASPNETCORE_ENVIRONMENT=Production dotnet run --no-launch-profile
