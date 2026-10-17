@echo off
setlocal
cd /d "%~dp0"
python -B src\main.py %*
exit /b %errorlevel%
