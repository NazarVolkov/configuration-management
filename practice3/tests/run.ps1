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

function Assert-UvmError([string[]]$Command, [string]$Message) {
    $ErrorActionPreference = 'Continue'
    $output = & $exe @Command 2>&1
    if ($LASTEXITCODE -ne 1 -or ($output -join "`n") -notlike "*$Message*") {
        throw "Expected '$Message', got '$output'."
    }
}

function Test-InvalidProgram([string[]]$Instructions, [string]$Message) {
    $source = Join-Path $project 'build/invalid.yaml'
    $program = Join-Path $project 'build/invalid.bin'
    $dump = Join-Path $project 'build/invalid.csv'
    [IO.File]::WriteAllLines($source, $Instructions)
    $null = Invoke-Uvm @('assemble', $source, $program)
    Assert-UvmError @('interpret', $program, $dump, '0', '1') $Message
}

function Test-Memory([string]$Fixture, [int]$First, [int]$Last, [string[]]$Expected) {
    $name = [IO.Path]::GetFileNameWithoutExtension($Fixture)
    $source = Join-Path $PSScriptRoot $Fixture
    $program = Join-Path $project "build/$name.bin"
    $dump = Join-Path $project "build/$name.csv"
    $null = Invoke-Uvm @('assemble', $source, $program)
    $null = Invoke-Uvm @('interpret', $program, $dump, $First.ToString(), $Last.ToString())
    Assert-Text ([IO.File]::ReadAllLines($dump)) (@('address,value') + $Expected) $name
    Write-Host "PASS: $name ($First..$Last)"
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

Test-Memory 'copy.yaml' 19 23 @('19,0', '20,7', '21,42', '22,513', '23,67108863')
Test-Memory 'copy.yaml' 100 104 @('100,7', '101,42', '102,513', '103,67108863', '104,0')
Test-Memory 'sqrt.yaml' 256 258 @('256,0', '257,12', '258,0')
Test-Memory 'sqrt.yaml' 65535 65535 @('65535,10')

Test-InvalidProgram @('- push: 144', '- sqrt: 1') 'at byte 4: stack underflow'
Test-InvalidProgram @('- push: 65535', '- push: 144', '- sqrt: 1') 'base + offset in 0..65535'
$fractionalBase = @('- push: 0', '- push: 2', '- sqrt: 0', '- load: 0', '- push: 9', '- sqrt: 0')
Test-InvalidProgram $fractionalBase 'requires a whole base address'
Write-Host 'PASS: invalid sqrt operands and destinations'
