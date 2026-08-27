@echo off
setlocal
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\tools\run_next_case_loop.ps1" -Count 10 %*
endlocal
