$ErrorActionPreference = 'Stop'
$script:passed = 0
$project = Split-Path -Parent $PSScriptRoot
$translator = Join-Path $project 'build/cfg5.exe'
$work = Join-Path ([IO.Path]::GetTempPath()) ('cfg5-tests-' + [Guid]::NewGuid().ToString('N'))
$utf8 = [Text.UTF8Encoding]::new($false)

function Invoke-Translator([string] $CommandLine) {
    $start = [Diagnostics.ProcessStartInfo]::new($translator, $CommandLine)
    $start.UseShellExecute = $false
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $start.StandardOutputEncoding = $utf8
    $start.StandardErrorEncoding = $utf8
    $process = [Diagnostics.Process]::Start($start)
    try {
        $output = $process.StandardOutput.ReadToEndAsync()
        $errors = $process.StandardError.ReadToEndAsync()
        $process.WaitForExit()
        return [pscustomobject]@{ Code = $process.ExitCode; Output = $output.Result; Errors = $errors.Result }
    } finally {
        $process.Dispose()
    }
}

function Confirm([bool] $Condition, [string] $Failure) {
    if (!$Condition) { throw $Failure }
}

function Assert-TranslationFile([string] $Name, [string] $Path, [string] $Expected, [string] $Option = '--input') {
    $result = Invoke-Translator "$Option `"$Path`""
    Confirm ($result.Code -eq 0) "$Name failed ($($result.Code)): $($result.Errors)"
    Confirm ($result.Errors -ceq '') "$Name wrote to stderr: $($result.Errors)"
    $actual = $result.Output.Replace("`r`n", "`n")
    $expectedText = $Expected.Replace("`r`n", "`n")
    if ($expectedText -and !$expectedText.EndsWith("`n")) { $expectedText += "`n" }
    Confirm ($actual -ceq $expectedText) "$Name mismatch.`nExpected:`n$expectedText`nActual:`n$actual"
    $script:passed++
}

function Assert-Translation([string] $Name, [string] $Source, [string] $Expected) {
    $path = Join-Path $work "$Name.cfg"
    [IO.File]::WriteAllText($path, $Source, $utf8)
    Assert-TranslationFile $Name $path $Expected
}

function Assert-InputError([string] $Name, [string] $Source, [string] $Diagnostic) {
    $path = Join-Path $work "$Name.cfg"
    [IO.File]::WriteAllText($path, $Source, $utf8)
    $result = Invoke-Translator "--input `"$path`""
    Confirm ($result.Code -eq 1) "$Name did not report an input error: $($result.Code)"
    Confirm ($result.Output -ceq '') "$Name wrote partial TOML: $($result.Output)"
    Confirm ($result.Errors -match $Diagnostic) "$Name gave an unexpected diagnostic: $($result.Errors)"
    $script:passed++
}

if (!(Test-Path -LiteralPath $translator)) { throw 'Run build.bat first.' }
. (Join-Path $PSScriptRoot 'parser.ps1')
. (Join-Path $PSScriptRoot 'evaluator.ps1')
. (Join-Path $PSScriptRoot 'cli.ps1')
. (Join-Path $PSScriptRoot 'examples.ps1')

New-Item -ItemType Directory -Path $work | Out-Null
try {
    Test-Parser
    Test-Evaluator
    Test-Cli
    Test-Examples
    "Passed $script:passed checks."
} finally {
    Get-ChildItem -LiteralPath $work -File | Remove-Item -Force
    Remove-Item -LiteralPath $work
}
