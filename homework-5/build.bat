@echo off
setlocal
cd /d "%~dp0"
where cl.exe >nul 2>&1
if errorlevel 1 (
    call :find_compiler
    if errorlevel 1 exit /b 1
)
set "parser_dir=build\deps\cpp-peglib"
call :prepare_parser
if errorlevel 1 exit /b 1
cl.exe /nologo /std:c++17 /Zc:__cplusplus /EHsc /W4 /WX /utf-8 /MT /O2 /DNOMINMAX /DWIN32_LEAN_AND_MEAN ^
    /external:I "%parser_dir%" /external:W0 /Fobuild\ /Febuild\cfg5.exe src\*.cpp
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
echo Install Visual Studio 2022 or Build Tools with Desktop development with C++. 1>&2
exit /b 1

:prepare_parser
if not exist "%parser_dir%\peglib.h" (
    git -c http.sslBackend=openssl -c advice.detachedHead=false clone --depth 1 --single-branch --branch v1.9.1 ^
        https://github.com/yhirose/cpp-peglib.git "%parser_dir%"
    if errorlevel 1 exit /b 1
)
set "parser_revision="
for /f %%I in ('git -C "%parser_dir%" rev-parse HEAD') do set "parser_revision=%%I"
if "%parser_revision%"=="527422aa38ce78c4214b21843e97584bc2db0150" exit /b 0
echo Unexpected cpp-peglib revision in %parser_dir%. 1>&2
exit /b 1
