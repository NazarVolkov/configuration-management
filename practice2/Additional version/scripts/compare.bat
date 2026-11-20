@echo off
setlocal
cd /d "%~dp0.."
for %%P in (Logging Options Injection) do (
    echo === %%P ===
    dotnet restore comparison\%%P\%%P.csproj --source https://api.nuget.org/v3/index.json
    if errorlevel 1 exit /b 1
    dotnet list comparison\%%P\%%P.csproj package --include-transitive
    if errorlevel 1 exit /b 1
)
exit /b 0
