@echo off
setlocal
cd /d "%~dp0.."
for %%C in (nuget options injection) do (
    call run.bat examples/%%C.json
    if errorlevel 1 exit /b 1
)
exit /b 0
