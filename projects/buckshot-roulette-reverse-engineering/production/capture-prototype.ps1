[CmdletBinding()]
param(
    [string]$GodotExecutable = 'C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe',
    [string]$FfprobeExecutable = 'C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffprobe.exe',
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9._-]*\.avi$')]
    [string]$OutputName = 'prototype-demo.avi',
    [switch]$Overwrite,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSVersion.Major -lt 7) { throw 'Use PowerShell 7 (pwsh) for safe ProcessStartInfo.ArgumentList handling.' }
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$prototypeRoot = Join-Path $projectRoot 'prototype'
$captureRoot = Join-Path $projectRoot 'captures'
$evidenceRoot = Join-Path $projectRoot 'production/local/test-evidence'
$outputPath = [IO.Path]::GetFullPath((Join-Path $captureRoot $OutputName))
$stem = [IO.Path]::GetFileNameWithoutExtension($OutputName)
$logPath = Join-Path $evidenceRoot "$stem-movie.log"
$manifestPath = Join-Path $evidenceRoot "$stem-capture.json"
$demoLog = Join-Path $projectRoot 'production/local/demo-events.json'
if (-not (Test-Path -LiteralPath $GodotExecutable -PathType Leaf)) {
    throw "Godot was not found. Pass -GodotExecutable with the installed Godot 4 executable path."
}
if (-not (Test-Path -LiteralPath $FfprobeExecutable -PathType Leaf)) {
    throw 'ffprobe is required to verify the actual movie format. Pass -FfprobeExecutable with its installed path.'
}
if (-not (Test-Path -LiteralPath (Join-Path $prototypeRoot 'project.godot') -PathType Leaf)) {
    throw "Prototype project is missing: $prototypeRoot"
}
if (-not $outputPath.StartsWith(([IO.Path]::GetFullPath($captureRoot) + [IO.Path]::DirectorySeparatorChar), [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Capture output must remain inside this project captures folder.'
}
if ((Test-Path -LiteralPath $outputPath) -and -not $Overwrite -and -not $DryRun) {
    throw "Capture already exists. Choose -OutputName or explicitly pass -Overwrite: $outputPath"
}

# Do not use --headless: this movie must contain GPU-rendered scene pixels.
# --fixed-fps is deterministic movie time, not a fast-forward time scale.
# Main's --demo normally quits itself after about 33.17 seconds (1,990 headless fixed-step frames). 5,400 frames
# is a 90-second safety ceiling, not the intended duration or a timer kill.
$godotArguments = @(
    '--path', $prototypeRoot,
    '--display-driver', 'windows', '--rendering-driver', 'opengl3',
    '--rendering-method', 'gl_compatibility',
    '--windowed', '--resolution', '1920x1080',
    '--write-movie', $outputPath,
    '--fixed-fps', '60', '--disable-vsync', '--quit-after', '5400',
    '--log-file', $logPath,
    '--', '--demo'
)
$record = [ordered]@{
    executable = $GodotExecutable
    arguments = $godotArguments
    output = $outputPath
    requestedWidth = 1920
    requestedHeight = 1080
    requestedFps = 60
    safetyCeilingFrames = 5400
    headless = $false
    waitsForGodotProcess = $true
    verifiesActualMediaFormat = $true
    captureKind = 'independently-authored-prototype-fixed-test'
    sourceGameplay = $false
    visualQualityApproved = $false
    startedAtUtc = $null
    finishedAtUtc = $null
    exitCode = $null
    status = 'prepared-not-executed'
}
if ($DryRun) { $record | ConvertTo-Json -Depth 5; return }
New-Item -ItemType Directory -Force -Path $captureRoot, $evidenceRoot | Out-Null
$record.startedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
$record.status = 'running'
$record | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 -LiteralPath $manifestPath
$startInfo = [System.Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $GodotExecutable
$startInfo.WorkingDirectory = $prototypeRoot
$startInfo.UseShellExecute = $false
$startInfo.CreateNoWindow = $true
foreach ($argument in $godotArguments) { $startInfo.ArgumentList.Add($argument) }
$process = [System.Diagnostics.Process]::Start($startInfo)
$record.processId = $process.Id
$record | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 -LiteralPath $manifestPath
$process.WaitForExit()
$record.exitCode = $process.ExitCode
$process.Dispose()
$record.finishedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
$startedUtc = [datetimeoffset]::Parse($record.startedAtUtc).UtcDateTime
$completedDemo = (Test-Path -LiteralPath $demoLog) -and ((Get-Item -LiteralPath $demoLog).LastWriteTimeUtc -ge $startedUtc)
$record.status = 'failed-or-demo-incomplete'
if (Test-Path -LiteralPath $outputPath) {
    $record.outputBytes = (Get-Item -LiteralPath $outputPath).Length
    $record.outputSha256 = (Get-FileHash -LiteralPath $outputPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $probeText = (& $FfprobeExecutable -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,avg_frame_rate:format=duration -of json $outputPath | Out-String)
    $record.probeExitCode = $LASTEXITCODE
    if ($record.probeExitCode -eq 0) {
        $probe = $probeText | ConvertFrom-Json
        $video = $probe.streams | Select-Object -First 1
        $record.actualWidth = $video.width
        $record.actualHeight = $video.height
        $record.actualFrameRate = $video.avg_frame_rate
        $record.actualDurationSeconds = [double]$probe.format.duration
        $formatMatches = $video.width -eq 1920 -and $video.height -eq 1080 -and $video.avg_frame_rate -eq '60/1'
        if (-not $formatMatches) {
            $record.status = 'failed-output-format'
        } elseif ($record.exitCode -eq 0 -and $completedDemo) {
            $record.status = 'format-verified-awaiting-audio-and-visual-qa'
        }
    }
}
if ($completedDemo) { Copy-Item -LiteralPath $demoLog -Destination (Join-Path $evidenceRoot "$stem-events.json") -Force }
$record | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 -LiteralPath $manifestPath
if ($record.status -ne 'format-verified-awaiting-audio-and-visual-qa') { throw "Movie failed: $($record.status). Inspect $logPath and $manifestPath" }
Write-Output "Movie format verified as 1920x1080/60; sound and picture review remain: $outputPath"
