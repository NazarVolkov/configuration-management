param([switch]$Images)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
Push-Location (Split-Path $PSScriptRoot -Parent)
$work = Join-Path ([IO.Path]::GetTempPath()) ('practice2-' + [guid]::NewGuid().ToString('N'))

function Get-CppGraph {
    param([string]$Name)
    $lines = & ./build/nuget_graph.exe "examples/$Name.json" --stage 3
    if ($LASTEXITCODE -ne 0) { throw "C++ analyzer failed for $Name" }
    $lines | Set-Content -Encoding UTF8 "output/comparison/$Name-cpp.txt"
    $graph = @{}
    foreach ($line in $lines) {
        $node, $children = $line -split ' -> ', 2
        $graph[$node] = if ($children -eq '-') { @() } else { @($children -split ' ') }
    }
    return $graph
}

function Get-NativeGraph {
    param([string]$Folder)
    $versions = @{}
    $requirements = @{}
    foreach ($archive in Get-ChildItem -LiteralPath $Folder -Recurse -Filter *.nupkg) {
        $zip = [IO.Compression.ZipFile]::OpenRead($archive.FullName)
        try {
            $entry = $zip.Entries | Where-Object { $_.FullName -like '*.nuspec' }
            $reader = New-Object IO.StreamReader($entry.Open())
            try { [xml]$xml = $reader.ReadToEnd() } finally { $reader.Dispose() }
            $meta = $xml.SelectSingleNode("//*[local-name()='metadata']")
            $id = $meta.SelectSingleNode("*[local-name()='id']").InnerText.ToLowerInvariant()
            $version = $meta.SelectSingleNode("*[local-name()='version']").InnerText
            $versions[$id] = "$id@$version"
            $deps = $meta.SelectSingleNode("*[local-name()='dependencies']")
            $group = $null
            if ($deps) {
                $group = $deps.SelectSingleNode("*[local-name()='group'][@targetFramework='net8.0']")
                if (-not $group) { $group = $deps }
            }
            $requirements[$id] = @()
            if ($group) {
                foreach ($dep in $group.SelectNodes("*[local-name()='dependency']")) {
                    $requirements[$id] += $dep.GetAttribute('id').ToLowerInvariant()
                }
            }
        } finally { $zip.Dispose() }
    }
    $graph = @{}
    foreach ($id in $versions.Keys) {
        $graph[$versions[$id]] = @()
        foreach ($dep in $requirements[$id]) {
            if (-not $versions.ContainsKey($dep)) { throw "Native dependency missing: $dep" }
            $graph[$versions[$id]] += $versions[$dep]
        }
    }
    return $graph
}

function Get-Edges {
    param([hashtable]$Graph)
    foreach ($node in $Graph.Keys) {
        foreach ($child in $Graph[$node]) { "$node -> $child" }
    }
}

try {
    if (-not (Test-Path build/nuget_graph.exe)) {
        & ./build.bat
        if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
    }
    New-Item -ItemType Directory -Force output/comparison | Out-Null
    $tool = Join-Path $PWD 'build/deps/nuget.exe'
    if (-not (Test-Path -LiteralPath $tool)) {
        & curl.exe -fLsS --max-time 60 -o $tool 'https://dist.nuget.org/win-x86-commandline/v6.11.1/nuget.exe'
        if ($LASTEXITCODE -ne 0) { throw 'Cannot download NuGet CLI' }
    }
    $examples = @{logging='Microsoft.Extensions.Logging';options='Microsoft.Extensions.Options';
        injection='Microsoft.Extensions.DependencyInjection'}
    foreach ($name in @('logging','options','injection')) {
        $package = $examples[$name]
        $folder = Join-Path $work $name
        $log = & $tool install $package -Version 8.0.0 -Framework net8.0 -OutputDirectory $folder `
            -Source https://api.nuget.org/v3/index.json -DependencyVersion Lowest `
            -NonInteractive -DirectDownload -NoHttpCache
        $code = $LASTEXITCODE
        $log | Set-Content -Encoding UTF8 "output/comparison/$name-nuget.txt"
        if ($code -ne 0) { throw "NuGet failed for $package" }
        $cpp = Get-CppGraph $name
        $native = Get-NativeGraph $folder
        $cppEdges = @(Get-Edges $cpp | Sort-Object)
        $nativeEdges = @(Get-Edges $native | Sort-Object)
        $nativeEdges | Set-Content -Encoding UTF8 "output/comparison/$name-native-edges.txt"
        if ((($cpp.Keys | Sort-Object) -join '|') -ne (($native.Keys | Sort-Object) -join '|') -or
            ($cppEdges -join '|') -ne ($nativeEdges -join '|')) {
            throw "Graphs differ for $package"
        }
        Write-Host "$package matches: $($cpp.Count) nodes, $($cppEdges.Count) edges."
        if ($Images) {
            & ./build/nuget_graph.exe "examples/$name.json" --no-open
            if ($LASTEXITCODE -ne 0) { throw "Image failed for $package" }
        }
    }
} finally {
    $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    $fullWork = [IO.Path]::GetFullPath($work)
    if ($fullWork.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase) -and
        (Split-Path $fullWork -Leaf) -like 'practice2-*' -and (Test-Path -LiteralPath $fullWork)) {
        Remove-Item -LiteralPath $fullWork -Recurse -Force
    }
    Pop-Location
}
