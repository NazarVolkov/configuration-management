$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
& (Join-Path $project 'build.bat')
if ($LASTEXITCODE -ne 0) { throw 'Build failed.' }

$exe = Join-Path $project 'build/uvm.exe'
$fixture = Join-Path $PSScriptRoot 'encoding.yaml'
$binary = Join-Path $project 'build/encoding.bin'

function Invoke-Uvm([string[]]$Command) {
    $output = & $exe @Command
    if ($LASTEXITCODE -ne 0) { throw "uvm failed: $($Command -join ' ')" }
    return $output
}

function Assert-Text([string[]]$Actual, [string[]]$Expected, [string]$Label) {
    if (($Actual -join "`n") -cne ($Expected -join "`n")) {
        throw "$Label differs. Expected [$($Expected -join '; ')], got [$($Actual -join '; ')]."
    }
}

$fields = Invoke-Uvm @('assemble', $fixture, $binary, '--test')
Assert-Text $fields @('A=14, B=285', 'A=6, B=759', 'A=3, B=547', 'A=11, B=15') 'Instruction fields'
Write-Host 'PASS: instruction fields'
