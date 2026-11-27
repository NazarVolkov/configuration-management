function Test-Examples {
    foreach ($example in @('greenhouse', 'warehouse')) {
        $source = Join-Path $project "examples/$example.cfg"
        $expected = Get-Content -LiteralPath (Join-Path $PSScriptRoot "$example.toml") -Encoding UTF8 -Raw
        Assert-TranslationFile $example $source $expected
    }
}
