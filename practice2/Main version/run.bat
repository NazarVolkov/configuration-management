@echo off
setlocal
cd /d "%~dp0"
if not exist build\nuget_graph.exe (
    call build.bat
    if errorlevel 1 exit /b 1
)
build\nuget_graph.exe %*
exit /b %errorlevel%
