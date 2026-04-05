@echo off
cd /d %~dp0
start "Literature Review Verifier API" cmd /k "%~dp0setup_and_run_api.bat"
start "Literature Review Verifier WebUI" cmd /k "%~dp0setup_and_run_webui.bat"
