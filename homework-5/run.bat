@echo off
setlocal
if not exist "%~dp0build\cfg5.exe" (
    echo Run build.bat first. 1>&2
    exit /b 1
)
"%~dp0build\cfg5.exe" %*
exit /b %errorlevel%
