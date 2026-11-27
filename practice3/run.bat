@echo off
setlocal
if not exist "%~dp0build\uvm.exe" (
    call "%~dp0build.bat"
    if errorlevel 1 exit /b 1
)
"%~dp0build\uvm.exe" %*
exit /b %errorlevel%
