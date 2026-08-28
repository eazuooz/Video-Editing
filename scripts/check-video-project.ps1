# Validates a project's manifest and the files needed for the requested stage.
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-video-project.ps1 -Project jump-physics
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-video-project.ps1 -Project jump-physics -Stage publish

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9]+(?:-[a-z0-9]+)*$')]
    [string]$Project,

    [ValidateSet('setup', 'publish')]
    [string]$Stage = 'setup'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$manifestPath = Join-Path $repoRoot "projects/$Project/project.json"
$failures = [System.Collections.Generic.List[string]]::new()

function Add-Failure([string]$Message) {
    $script:failures.Add($Message)
    Write-Host "FAIL $Message" -ForegroundColor Red
}

function Add-Pass([string]$Message) {
    Write-Host " OK  $Message" -ForegroundColor Green
}

function Resolve-RepoPath([string]$RelativePath) {
    $fullPath = [System.IO.Path]::GetFullPath((Join-Path $repoRoot $RelativePath))
    $rootPrefix = $repoRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
    if (-not $fullPath.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Path escapes the repository: $RelativePath"
    }
    return $fullPath
}

function Test-ManifestFile([object]$Paths, [string]$Key) {
    $property = $Paths.PSObject.Properties[$Key]
    if ($null -eq $property -or [string]::IsNullOrWhiteSpace([string]$property.Value)) {
        Add-Failure "project.json paths.$Key is empty"
        return $null
    }

    $fullPath = Resolve-RepoPath ([string]$property.Value)
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        Add-Failure "Missing paths.$Key file: $($property.Value)"
        return $null
    }

    Add-Pass "paths.$Key -> $($property.Value)"
    return $fullPath
}

function Test-Srt([string]$Path, [string]$Label) {
    $lines = Get-Content -LiteralPath $Path -Encoding utf8
    $numbers = @($lines | Where-Object { $_ -match '^\d+$' } | ForEach-Object { [int]$_ })
    $timings = @($lines | Where-Object {
        $_ -match '^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$'
    })

    if ($numbers.Count -eq 0 -or $numbers.Count -ne $timings.Count) {
        Add-Failure "$Label is not a valid numbered SRT ($($numbers.Count) numbers, $($timings.Count) timings)"
        return
    }

    for ($index = 0; $index -lt $numbers.Count; $index++) {
        if ($numbers[$index] -ne ($index + 1)) {
            Add-Failure "$Label numbering breaks at entry $($index + 1)"
            return
        }
    }

    Add-Pass "$Label contains $($numbers.Count) sequential captions"
}

if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Project manifest not found: $manifestPath"
}

try {
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json
    Add-Pass 'project.json is valid JSON'
} catch {
    throw "Invalid project.json: $($_.Exception.Message)"
}

if ($manifest.slug -ne $Project) {
    Add-Failure "Manifest slug '$($manifest.slug)' does not match folder '$Project'"
} else {
    Add-Pass "manifest slug is $Project"
}

$setupKeys = @('script', 'sources', 'publishingKo', 'publishingEn', 'motionCanvasProject', 'manimProject')
$resolved = @{}
foreach ($key in $setupKeys) {
    $resolved[$key] = Test-ManifestFile $manifest.paths $key
}

if ($null -ne $resolved.script) {
    try {
        $scriptData = Get-Content -LiteralPath $resolved.script -Raw -Encoding utf8 | ConvertFrom-Json
        $sceneCount = @($scriptData.scenes).Count
        if ($sceneCount -lt 1) {
            Add-Failure 'Narration script has no scenes'
        } else {
            Add-Pass "narration script contains $sceneCount scenes"
        }
    } catch {
        Add-Failure "Narration script is invalid JSON: $($_.Exception.Message)"
    }
}

if ($Stage -eq 'publish') {
    $publishKeys = @('narration', 'captionsKo', 'captionsEn', 'videoClean')
    foreach ($key in $publishKeys) {
        $resolved[$key] = Test-ManifestFile $manifest.paths $key
    }

    if ($null -ne $resolved.captionsKo) {
        Test-Srt $resolved.captionsKo 'Korean SRT'
    }
    if ($null -ne $resolved.captionsEn) {
        Test-Srt $resolved.captionsEn 'English SRT'
    }

    $ffprobe = Get-Command ffprobe -ErrorAction SilentlyContinue
    if ($null -ne $ffprobe -and $null -ne $resolved.videoClean) {
        try {
            $probeJson = & $ffprobe.Source -v error -select_streams v:0 `
                -show_entries stream=width,height,r_frame_rate -show_entries format=duration `
                -of json $resolved.videoClean
            $probe = $probeJson | ConvertFrom-Json
            $stream = @($probe.streams)[0]
            $duration = [double]$probe.format.duration
            Add-Pass "video is $($stream.width)x$($stream.height), $($stream.r_frame_rate), $([math]::Round($duration, 2))s"
        } catch {
            Add-Failure "ffprobe could not inspect the final video: $($_.Exception.Message)"
        }
    } elseif ($null -eq $ffprobe) {
        Write-Host 'SKIP ffprobe is not installed; media metadata was not checked' -ForegroundColor Yellow
    }
}

Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host "Project check failed with $($failures.Count) issue(s)." -ForegroundColor Red
    exit 1
}

Write-Host "Project '$Project' passed the '$Stage' checks." -ForegroundColor Green
