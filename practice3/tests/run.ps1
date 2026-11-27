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

$fields = Invoke-Uvm @('assemble', $fixture, $binary, '--test-fields')
$expectedFields = @('A=14, B=285', 'A=6, B=759', 'A=3, B=547', 'A=11, B=15', 'Binary size: 16 bytes')
Assert-Text $fields $expectedFields 'Instruction fields'
Write-Host 'PASS: instruction fields'

$bytes = Invoke-Uvm @('assemble', $fixture, $binary, '--test')
$expectedBytes = @(
    '0xDE, 0x11, 0x00, 0x00'
    '0x76, 0x2F, 0x00, 0x00'
    '0x33, 0x22, 0x00, 0x00'
    '0xFB, 0x00, 0x00, 0x00'
    'Binary size: 16 bytes'
)
Assert-Text $bytes $expectedBytes 'Displayed machine code'
$actualHex = [BitConverter]::ToString([IO.File]::ReadAllBytes($binary))
Assert-Text $actualHex 'DE-11-00-00-76-2F-00-00-33-22-00-00-FB-00-00-00' 'Binary file'
Write-Host 'PASS: machine code'
