[CmdletBinding()]
param(
    [string]$GodotExecutable = 'C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe',
    [switch]$Demo,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSVersion.Major -lt 7) { throw 'Use PowerShell 7 (pwsh) for safe ProcessStartInfo.ArgumentList handling.' }
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$prototypeRoot = Join-Path $projectRoot 'prototype'
$runtimeRoot = Join-Path $projectRoot 'production/local/prototype-runtime'
$logPath = Join-Path $runtimeRoot 'prototype.log'
if (-not (Test-Path -LiteralPath $GodotExecutable -PathType Leaf)) {
    throw "Godot was not found. Pass -GodotExecutable with the installed Godot 4 executable path."
}
if (-not (Test-Path -LiteralPath (Join-Path $prototypeRoot 'project.godot') -PathType Leaf)) {
    throw "Prototype project is missing: $prototypeRoot"
}

# Array arguments are passed directly; no command-string evaluation or global settings.
$godotArguments = @(
    '--path', $prototypeRoot,
    '--windowed', '--resolution', '1920x1080',
    '--rendering-method', 'gl_compatibility',
    '--log-file', $logPath
)
if ($Demo) { $godotArguments += @('--', '--demo') }
if ($DryRun) {
    [ordered]@{ executable = $GodotExecutable; arguments = $godotArguments; writes = @($logPath, 'ordinary Godot runtime/cache'); launchesWindow = $true } | ConvertTo-Json -Depth 5
    return
}
New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null
$startInfo = [System.Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $GodotExecutable
$startInfo.WorkingDirectory = $prototypeRoot
$startInfo.UseShellExecute = $false
$startInfo.CreateNoWindow = $true
foreach ($argument in $godotArguments) { $startInfo.ArgumentList.Add($argument) }
$process = [System.Diagnostics.Process]::Start($startInfo)
$process.WaitForExit()
$gameExitCode = $process.ExitCode
$process.Dispose()
if ($gameExitCode -ne 0) { throw "Godot exited with code $gameExitCode. See $logPath" }
