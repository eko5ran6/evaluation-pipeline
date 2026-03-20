@echo off
REM Start the frontend dashboard using the repository's backend venv.
setlocal

set "REPO_ROOT=%~dp0.."
set "PY=%REPO_ROOT%\backend\venv\Scripts\python.exe"

if not exist "%PY%" (
  echo Python not found at "%PY%"
  echo Activate the venv or run 'pip install -r backend\requirements.txt' first.
  exit /b 1
)

"%PY%" -m backend.server

