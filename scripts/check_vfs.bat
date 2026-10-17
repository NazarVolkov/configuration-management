@echo off
setlocal
cd /d "%~dp0.."
for %%V in (minimal demo deep) do (
    echo === VFS: %%V ===
    call run.bat --config config.yaml --vfs vfs/%%V --startup scripts/startup_stage3.txt <nul
    if errorlevel 1 exit /b 1
)
exit /b 0
