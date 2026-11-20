@echo off
setlocal
cd /d "%~dp0"
where cl >nul 2>&1
if errorlevel 1 (
    call :compiler
    if errorlevel 1 exit /b 1
)
if not exist build\deps mkdir build\deps
if not exist build\deps\json.hpp (
    curl.exe -fLsS --max-time 60 --output build\deps\json.tmp ^
        https://raw.githubusercontent.com/nlohmann/json/v3.12.0/single_include/nlohmann/json.hpp
    if errorlevel 1 exit /b 1
    move /y build\deps\json.tmp build\deps\json.hpp >nul
    if errorlevel 1 exit /b 1
)
call :xml tinyxml2.h
if errorlevel 1 exit /b 1
call :xml tinyxml2.cpp
if errorlevel 1 exit /b 1
cl /nologo /std:c++17 /EHsc /W4 /WX /utf-8 /MT /Ibuild\deps /Fobuild\ ^
    /Febuild\nuget_graph.exe src\*.cpp build\deps\tinyxml2.cpp winhttp.lib shell32.lib
exit /b %errorlevel%

:compiler
set "vswhere=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%vswhere%" goto missing
set "vs="
set "component=Microsoft.VisualStudio.Component.VC.Tools.x86.x64"
for /f "usebackq delims=" %%V in (`"%vswhere%" -latest -products * -requires %component% ^
    -property installationPath`) do set "vs=%%V"
if not defined vs goto missing
call "%vs%\VC\Auxiliary\Build\vcvars64.bat" >nul
exit /b %errorlevel%

:missing
echo Install Visual Studio with Desktop development with C++.
exit /b 1

:xml
if exist "build\deps\%~1" exit /b 0
curl.exe -fLsS --max-time 60 --output "build\deps\%~1.tmp" ^
    "https://raw.githubusercontent.com/leethomason/tinyxml2/11.0.0/%~1"
if errorlevel 1 exit /b 1
move /y "build\deps\%~1.tmp" "build\deps\%~1" >nul
exit /b %errorlevel%
