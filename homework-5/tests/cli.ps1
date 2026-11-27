function Test-InvocationError([string] $CommandLine, [int] $Code, [string] $Message) {
    $result = Invoke-Translator $CommandLine
    Confirm ($result.Code -eq $Code) "Unexpected code for $($CommandLine): $($result.Code)"
    Confirm ($result.Output -ceq '') "Unexpected stdout for $($CommandLine): $($result.Output)"
    Confirm ($result.Errors -match $Message) "Unexpected diagnostic for $($CommandLine): $($result.Errors)"
    $script:passed++
}

function Test-Cli {
    foreach ($option in @('--help', '-h')) {
        $result = Invoke-Translator $option
        Confirm ($result.Code -eq 0 -and $result.Output -match 'Usage: cfg5.exe') "Help failed for $option"
        Confirm ($result.Errors -ceq '') "Help wrote to stderr for $option"
        $script:passed++
    }

    Test-InvocationError '' 2 'expected --input'
    Test-InvocationError '--input' 2 'expected --input'
    Test-InvocationError '--unknown input.cfg' 2 'expected --input'
    Test-InvocationError '--input input.cfg extra' 2 'expected --input'
    $missing = Join-Path $work 'does not exist.cfg'
    Test-InvocationError "--input `"$missing`"" 1 'cannot open input file'

    $unicode = [string][char]0x042F + [char]0x0437
    $file = Join-Path $work "$unicode config.cfg"
    [IO.File]::WriteAllText($file, "a: '$unicode'`r`n", [Text.UTF8Encoding]::new($true))
    Assert-TranslationFile 'UTF-8 BOM and Unicode path' $file "a = `"$unicode`"" '-i'

    [IO.File]::WriteAllBytes($file, [byte[]]@(0x61, 0x3A, 0x20, 0x27, 0xFF, 0x27))
    Test-InvocationError "--input `"$file`"" 1 'input must be valid UTF-8'

    $text = 'a: ' + "'" + [char]0x09 + [char]0x01 + [char]0x7F + "'"
    Assert-Translation 'TOML control escapes' $text 'a = "\u0009\u0001\u007F"'
    Assert-Translation 'TOML preserves floats' 'a: [4., -0.0, 1e-200]' 'a = [4.0, -0.0, 1e-200]'

    $output = & (Join-Path $project 'run.bat') --help
    Confirm ($LASTEXITCODE -eq 0 -and ($output -join "`n") -match 'Usage: cfg5.exe') 'run.bat did not start cfg5.exe'
    $script:passed++
}
