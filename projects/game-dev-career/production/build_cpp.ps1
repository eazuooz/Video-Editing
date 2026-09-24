$ErrorActionPreference = 'Stop'
$root = Resolve-Path "$PSScriptRoot/../../.."
$build = Join-Path $PSScriptRoot 'cpp-build'
New-Item -ItemType Directory -Force -Path $build | Out-Null
$vs = & 'C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe' -latest -products * -property installationPath
$vcvars = Join-Path $vs 'VC/Auxiliary/Build/vcvars64.bat'
$source = Join-Path $PSScriptRoot 'chest.cpp'
$exe = Join-Path $build 'chest.exe'
Push-Location $build
try {
    & cmd /d /s /c "call `"$vcvars`" >nul && cl /nologo /EHsc /std:c++17 /W4 /Fe:`"$exe`" `"$source`""
    if ($LASTEXITCODE -ne 0) { throw 'C++ build failed' }
    $result = & $exe
    if ($LASTEXITCODE -ne 0) { throw 'C++ tests failed' }
    $result | ConvertFrom-Json | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $root 'motion-canvas/src/projects/game-dev-career/cpp-trace.generated.json'), $result, [System.Text.UTF8Encoding]::new($false))
    Write-Output $result
} finally { Pop-Location }
