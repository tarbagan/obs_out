param(
    [ValidateSet('Release', 'RelWithDebInfo', 'Debug')]
    [string]$Configuration = 'RelWithDebInfo',
    [string]$Generator = '',
    [switch]$PrepareOnly
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$lock = Get-Content -Raw (Join-Path $projectRoot 'upstream.lock.json') | ConvertFrom-Json
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'Install Python 3.10 or newer.' }
& python (Join-Path $PSScriptRoot 'prepare.py')
if ($LASTEXITCODE -ne 0) { throw 'OBS source preparation failed.' }
if ($PrepareOnly) { return }
if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) {
    throw 'CMake 3.30+ is required. Run from a Visual Studio Developer PowerShell with CMake in PATH.'
}
if (-not $Generator) {
    $capabilities = (& cmake -E capabilities | ConvertFrom-Json)
    $generators = @($capabilities.generators | ForEach-Object { $_.name })
    $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
    if (-not (Test-Path -LiteralPath $vswhere)) { throw 'Install Visual Studio C++ Build Tools.' }
    $instance = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationVersion
    if (-not $instance) { throw 'Visual Studio is installed without the Desktop development with C++ workload.' }
    $majorVersion = ([version]$instance).Major
    $Generator = if ($majorVersion -ge 18) { 'Visual Studio 18 2026' } else { 'Visual Studio 17 2022' }
    if ($Generator -notin $generators) { throw "Update CMake: generator $Generator is unavailable." }
}
$sourceTree = Join-Path $projectRoot ".deps/obs-studio-$($lock.commit)"
$buildTree = Join-Path $projectRoot 'build/windows-x64'
& cmake -S $sourceTree -B $buildTree -G $Generator -A x64 `
    -DENABLE_FRONTEND=OFF -DENABLE_SCRIPTING=OFF -DENABLE_BROWSER=OFF `
    -DENABLE_VIRTUALCAM=OFF -DENABLE_DECKLINK=ON "-DOBS_VERSION_OVERRIDE=$($lock.version)"
if ($LASTEXITCODE -ne 0) { throw 'CMake configuration failed.' }
& cmake --build $buildTree --config $Configuration --target decklink decklink-output-ui --parallel
if ($LASTEXITCODE -ne 0) { throw 'Compilation failed.' }
$packageRoot = Join-Path $projectRoot "dist/obs-out-$($lock.version)-windows-x64"
$binaryDir = Join-Path $packageRoot 'obs-plugins/64bit'
New-Item -ItemType Directory -Force $binaryDir | Out-Null
foreach ($module in @('decklink', 'decklink-output-ui')) {
    $binary = Join-Path $buildTree "plugins/$module/$Configuration/$module.dll"
    if (-not (Test-Path -LiteralPath $binary)) { throw "Expected binary missing: $binary" }
    Copy-Item -LiteralPath $binary -Destination $binaryDir -Force
    $data = Join-Path $packageRoot "data/obs-plugins/$module"
    New-Item -ItemType Directory -Force $data | Out-Null
    Copy-Item -Path (Join-Path $projectRoot "plugins/$module/data/*") -Destination $data -Recurse -Force
}
Copy-Item -LiteralPath (Join-Path $projectRoot 'COPYING') -Destination $packageRoot -Force
Copy-Item -LiteralPath (Join-Path $projectRoot 'THIRD_PARTY.md') -Destination $packageRoot -Force
Copy-Item -LiteralPath (Join-Path $projectRoot 'plugins/decklink/LICENSE.decklink-sdk') -Destination $packageRoot -Force
Copy-Item -LiteralPath (Join-Path $projectRoot 'README.md') -Destination $packageRoot -Force
Copy-Item -LiteralPath (Join-Path $projectRoot 'docs') -Destination $packageRoot -Recurse -Force
Write-Host "Package ready: $packageRoot"
Write-Host 'Use a separate OBS 32.2.2 test copy. These modules replace the built-in DeckLink modules.'
