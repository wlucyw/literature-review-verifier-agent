@echo off
cd /d %~dp0
if not exist .venv\Scripts\python.exe (
  echo Virtual environment not found at .venv\Scripts\python.exe
  echo Please create it first: python -m venv .venv
  exit /b 1
)
call .venv\Scripts\activate.bat
python scripts\run_demo.py
