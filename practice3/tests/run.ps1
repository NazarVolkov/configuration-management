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

function Assert-Dump([string]$Path, [int]$First, [double[]]$Expected) {
    $lines = [IO.File]::ReadAllLines($Path)
    if ($lines.Length -ne $Expected.Length + 1 -or $lines[0] -cne 'address,value') {
        throw "Invalid CSV header or row count in $Path."
    }
    $culture = [Globalization.CultureInfo]::InvariantCulture
    $tolerance = 1e-12
    for ($index = 0; $index -lt $Expected.Length; $index++) {
        $address = $First + $index
        $columns = $lines[$index + 1] -split ','
        if ($columns.Length -ne 2 -or $columns[0] -cne [string]$address) {
            throw "Expected CSV address $address in $Path."
        }
        $value = [double]::Parse($columns[1], $culture)
        if ([double]::IsNaN($value) -or [math]::Abs($value - $Expected[$index]) -gt $tolerance) {
            throw "Address $address in $Path has $value, expected $($Expected[$index])."
        }
    }
}

function Test-Memory([string]$Fixture, [int]$First, [double[]]$Expected) {
    $name = [IO.Path]::GetFileNameWithoutExtension($Fixture)
    $source = Join-Path $PSScriptRoot $Fixture
    $program = Join-Path $project "build/$name.bin"
    $dump = Join-Path $project "build/$name.csv"
    $last = $First + $Expected.Length - 1
    $null = Invoke-Uvm @('assemble', $source, $program)
    $null = Invoke-Uvm @('interpret', $program, $dump, $First.ToString(), $last.ToString())
    Assert-Dump $dump $First $Expected
    Write-Host "PASS: $name ($First..$last)"
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

Test-Memory 'copy.yaml' 19 @(0, 7, 42, 513, 67108863)
Test-Memory 'copy.yaml' 100 @(7, 42, 513, 67108863, 0)
Test-Memory 'sqrt.yaml' 256 @(0, 12, 0)
Test-Memory 'sqrt.yaml' 65535 @(10)

Test-InvalidProgram @('- push: 144', '- sqrt: 1') 'at byte 4: stack underflow'
Test-InvalidProgram @('- push: 65535', '- push: 144', '- sqrt: 1') 'base + offset in 0..65535'
$fractionalBase = @('- push: 0', '- push: 2', '- sqrt: 0', '- load: 0', '- push: 9', '- sqrt: 0')
Test-InvalidProgram $fractionalBase 'requires a whole base address'
Write-Host 'PASS: invalid sqrt operands and destinations'

Test-Memory 'vector-squares.yaml' 10 @(1, 4, 9, 16, 25, 36, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6)
Test-Memory 'vector-mixed.yaml' 10 @(
    0, 2, 8, 49, 121, 256, 0, 0, 0, 0, 0, 1.4142135623730951, 2.8284271247461903, 7, 11, 16
)
Test-Memory 'vector-large.yaml' 10 @(
    100, 1024, 10000, 1000000, 16777216, 67092481, 0, 0, 0, 0, 10, 32, 100, 1000, 4096, 8191
)

$invalidSource = Join-Path $project 'build/invalid.yaml'
$invalidBinary = Join-Path $project 'build/invalid.bin'
$invalidDump = Join-Path $project 'build/invalid.csv'
[IO.File]::WriteAllLines($invalidSource, [string[]]@('# address overflow', '- load: 65536'))
Assert-UvmError @('assemble', $invalidSource, $invalidBinary) ':2: expected an integer in 0..65535'
[IO.File]::WriteAllBytes($invalidBinary, [byte[]]@(0xDE, 0x11, 0x00))
Assert-UvmError @('interpret', $invalidBinary, $invalidDump, '0', '1') 'at byte 0: truncated instruction'
[IO.File]::WriteAllBytes($invalidBinary, [byte[]]@(0x00, 0x00, 0x00, 0x00))
Assert-UvmError @('interpret', $invalidBinary, $invalidDump, '0', '1') 'at byte 0: unknown opcode 0'
[IO.File]::WriteAllBytes($invalidBinary, [byte[]]@(0x06, 0x00, 0x10, 0x00))
Assert-UvmError @('interpret', $invalidBinary, $invalidDump, '0', '1') 'at byte 0: nonzero reserved bits'
Assert-UvmError @('interpret', $binary, $invalidDump, '1', '0') 'expected an increasing or single-address range'
Write-Host 'PASS: invalid source, machine code, and dump range'
