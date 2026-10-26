@echo off
setlocal
cd /d "%~dp0.."
echo === Settings from config.yaml ===
call run.bat <nul
if errorlevel 1 exit /b 1
echo === CLI overrides YAML: minimal VFS and another startup script ===
call run.bat --config config.yaml --vfs vfs/minimal --startup scripts/startup_stage3.txt <nul
if errorlevel 1 exit /b 1
echo === All CLI parameters with deep VFS ===
call run.bat --config config.yaml --vfs vfs/deep --startup scripts/startup_stage3.txt <nul
if errorlevel 1 exit /b 1
exit /b 0
