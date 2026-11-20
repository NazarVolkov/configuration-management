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
    return ,@($lines | ForEach-Object { "$_" })
}

function Save-Config {
    param([hashtable]$Settings)
    $Settings | ConvertTo-Json | Set-Content -Encoding UTF8 build/test.json
}

try {
    & ./build.bat
    if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
    $actual = Invoke-App @('--stage','1')
    foreach ($line in @('package = A', 'test_mode = true', 'ascii_tree = true')) {
        if ($actual -notcontains $line) { throw "Missing setting: $line" }
    }
    $valid = @{package='A';repository='../tests/repository.json';test_mode=$true;ascii_tree=$true}
    $invalid = @{package='bad name';repository='missing.json';test_mode='true';ascii_tree=1}
    foreach ($key in $invalid.Keys) {
        $changed = $valid.Clone()
        $changed[$key] = $invalid[$key]
        Save-Config $changed
        $null = Invoke-App @('build/test.json','--stage','1') $false
        $changed = $valid.Clone()
        $changed.Remove($key)
        Save-Config $changed
        $null = Invoke-App @('build/test.json','--stage','1') $false
    }
    $changed = $valid.Clone()
    $changed.test_mode = $false
    $changed.repository = 'not-a-url'
    Save-Config $changed
    $null = Invoke-App @('build/test.json','--stage','1') $false
    '{invalid' | Set-Content -Encoding UTF8 build/test.json
    $null = Invoke-App @('build/test.json','--stage','1') $false
    $null = Invoke-App @('missing.json') $false
    $actual = Invoke-App @('--stage','3')
    if (($actual -join '|') -ne 'A -> B C|B -> D|C -> D|D -> -') { throw 'Branch DFS failed' }
    $cases = @{
        E = 'E -> F|F -> E'
        G = 'G -> -'
        H = 'H -> H'
    }
    foreach ($name in $cases.Keys) {
        $changed = $valid.Clone()
        $changed.package = $name
        Save-Config $changed
        $actual = Invoke-App @('build/test.json','--stage','3')
        if (($actual -join '|') -ne $cases[$name]) { throw "DFS failed for $name" }
    }
    '{"A":["Z"]}' | Set-Content -Encoding UTF8 build/broken.json
    $changed = $valid.Clone()
    $changed.repository = 'broken.json'
    Save-Config $changed
    $null = Invoke-App @('build/test.json','--stage','3') $false
    $actual = Invoke-App @('--stage','4','--reverse','D')
    if (($actual -join '|') -ne 'A -> -|B -> A I|C -> A|D -> B C|I -> -') {
        throw 'Reverse graph lost incoming packages outside the root subtree'
    }
    $cases = @{E='E -> F|F -> E';G='G -> -';H='H -> H'}
    foreach ($name in $cases.Keys) {
        $actual = Invoke-App @('--stage','4','--reverse',$name)
        if (($actual -join '|') -ne $cases[$name]) { throw "Reverse DFS failed for $name" }
    }
    $null = Invoke-App @('--stage','4','--reverse','Z') $false
    $null = Invoke-App @('--stage','3','--reverse','D') $false
    $actual = Invoke-App @('--no-image')
    if ("$actual" -notmatch 'D \[shown\]') { throw 'Shared dependency marker missing' }
    $diagram = Get-Content -Raw output/graph_A.puml
    foreach ($edge in @('P0 --> P1','P0 --> P2','P1 --> P3','P2 --> P3')) {
        if ($diagram -notmatch [regex]::Escape($edge)) { throw "PlantUML edge missing: $edge" }
    }
    $changed = $valid.Clone()
    $changed.package = 'E'
    Save-Config $changed
    $actual = Invoke-App @('build/test.json','--no-image')
    if ("$actual" -notmatch 'E \[cycle\]') { throw 'Cycle marker missing' }
    $changed.package = 'G'
    $changed.ascii_tree = $false
    Save-Config $changed
    $actual = Invoke-App @('build/test.json','--no-image')
    if ($actual.Count -ne 1 -or $actual[0] -notmatch '^PlantUML: ') { throw 'Tree flag ignored' }
    $null = Invoke-App @('--stage','2')
    $null = Invoke-App @('--stage','0') $false
    $null = Invoke-App @('--stage') $false
    $null = Invoke-App @('--unknown') $false
    Write-Host "Passed $script:checks checks."
} finally {
    foreach ($name in @('build/test.json','build/broken.json','output/graph_E.puml','output/graph_G.puml')) {
        if (Test-Path -LiteralPath $name) { Remove-Item -LiteralPath $name -Force }
    }
    Pop-Location
}
