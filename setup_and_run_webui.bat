@echo off
cd /d %~dp0
set PYTHONUTF8=1

echo [1/3] Checking virtual environment...
if not exist .venv\Scripts\python.exe (
  echo Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
  )
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
  echo Failed to activate virtual environment.
  pause
  exit /b 1
)

echo [2/3] Installing dependencies if needed...
if not exist .venv\.deps_installed (
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
  )
  type nul > .venv\.deps_installed
)

echo [3/3] Starting Streamlit...
python -m streamlit run webui\streamlit_app.py
pause
