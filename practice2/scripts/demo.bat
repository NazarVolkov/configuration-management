@echo off
setlocal
cd /d "%~dp0.."
call run.bat --stage 1
if errorlevel 1 exit /b 1
call run.bat --stage 2
if errorlevel 1 exit /b 1
call run.bat --stage 3
if errorlevel 1 exit /b 1
call run.bat examples/config_cycle.json --stage 3
if errorlevel 1 exit /b 1
call run.bat examples/config_leaf.json --stage 3
if errorlevel 1 exit /b 1
call run.bat --stage 4 --reverse D
if errorlevel 1 exit /b 1
call run.bat examples/config_cycle.json --stage 4 --reverse B
if errorlevel 1 exit /b 1
call run.bat --no-image
exit /b %errorlevel%
