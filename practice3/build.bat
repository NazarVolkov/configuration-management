@echo off
setlocal
cd /d "%~dp0"
where cl.exe >nul 2>&1
if errorlevel 1 (
    call :find_compiler
    if errorlevel 1 exit /b 1
)
if not exist build mkdir build
cl.exe /nologo /std:c++17 /EHsc /W4 /WX /utf-8 /MT /Fobuild\ /Febuild\uvm.exe src\*.cpp
exit /b %errorlevel%

:find_compiler
set "vswhere=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
set "component=Microsoft.VisualStudio.Component.VC.Tools.x86.x64"
set "vs="
if not exist "%vswhere%" goto missing_compiler
set "vs_args=-latest -products * -requires %component% -property installationPath"
for /f "usebackq delims=" %%V in (`"%vswhere%" %vs_args%`) do set "vs=%%V"
if not defined vs goto missing_compiler
call "%vs%\VC\Auxiliary\Build\vcvars64.bat" >nul
exit /b %errorlevel%

:missing_compiler
echo Install Visual Studio or Build Tools with Desktop development with C++. 1>&2
exit /b 1
