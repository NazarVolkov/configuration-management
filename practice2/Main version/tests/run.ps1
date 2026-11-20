$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
$script:checks = 0

function Invoke-App {
    param([string[]]$Options, [bool]$Success = $true)
    $saved = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $lines = & ./build/nuget_graph.exe @Options 2>&1
    $code = $LASTEXITCODE
    $ErrorActionPreference = $saved
    if (($code -eq 0) -ne $Success) { throw "Unexpected exit code ${code}: $lines" }
    if (-not $Success -and "$lines" -notmatch 'Error:') { throw 'Missing error message' }
    $script:checks++
    return @($lines | ForEach-Object { "$_" })
}

function Save-Config {
    param([hashtable]$Settings)
    $Settings | ConvertTo-Json | Set-Content -Encoding UTF8 build/test.json
}

try {
    & ./build.bat
    if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
    $actual = Invoke-App
    foreach ($line in @('package = A', 'test_mode = true', 'ascii_tree = true')) {
        if ($actual -notcontains $line) { throw "Missing setting: $line" }
    }
    $valid = @{package='A';repository='../tests/repository.json';test_mode=$true;ascii_tree=$true}
    $invalid = @{package='bad name';repository='missing.json';test_mode='true';ascii_tree=1}
    foreach ($key in $invalid.Keys) {
        $changed = $valid.Clone()
        $changed[$key] = $invalid[$key]
        Save-Config $changed
        $null = Invoke-App @('build/test.json') $false
        $changed = $valid.Clone()
        $changed.Remove($key)
        Save-Config $changed
        $null = Invoke-App @('build/test.json') $false
    }
    $changed = $valid.Clone()
    $changed.test_mode = $false
    $changed.repository = 'not-a-url'
    Save-Config $changed
    $null = Invoke-App @('build/test.json') $false
    '{invalid' | Set-Content -Encoding UTF8 build/test.json
    $null = Invoke-App @('build/test.json') $false
    $null = Invoke-App @('missing.json') $false
    Write-Host "Passed $script:checks checks."
} finally {
    Pop-Location
}
