@echo off
echo ==========================================
echo      DataCleanPro  v1.0
echo ==========================================

set ROOT=%~dp0
set EXE=%ROOT%backend\dist\datacleanpro_api.exe
set VENV_PY=%ROOT%backend\venv\Scripts\python.exe

if not exist "%EXE%" if not exist "%VENV_PY%" (
  echo.
  echo No exe found - setting up Python venv as fallback...
  cd /d "%ROOT%backend"
  python -m venv venv
  venv\Scripts\pip install --upgrade pip -q
  venv\Scripts\pip install -r requirements.txt -q
  echo Done. Run: cd backend ^&^& python build_exe.py  to build the exe.
)

if exist "%EXE%" (
  echo   API engine : %EXE%  [exe mode]
) else (
  echo   API engine : Python venv  [fallback mode]
)

echo.
echo Starting DataCleanPro on http://localhost:5000
echo Press Ctrl+C to stop everything.
echo.

start "" http://localhost:5000
cd /d "%ROOT%frontend"
set ASPNETCORE_ENVIRONMENT=Production
dotnet run --no-launch-profile
