@echo off
echo ==========================================
echo  DataCleanPro - Build API Executable
echo ==========================================

set ROOT=%~dp0
set VENV_PY=%ROOT%backend\venv\Scripts\python.exe

if not exist "%VENV_PY%" (
  echo.
  echo Setting up Python venv first...
  cd /d "%ROOT%backend"
  python -m venv venv
  venv\Scripts\pip install --upgrade pip -q
  venv\Scripts\pip install -r requirements.txt -q
)

echo.
echo Building exe...
cd /d "%ROOT%backend"
"%VENV_PY%" build_exe.py

if exist "%ROOT%backend\dist\datacleanpro_api.exe" (
  echo.
  echo Done! Run run.bat to start DataCleanPro.
)
pause
