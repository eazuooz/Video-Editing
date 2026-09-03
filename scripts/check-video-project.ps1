# Validates a project's manifest and the files needed for the requested stage.
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-video-project.ps1 -Project jump-physics
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-video-project.ps1 -Project jump-physics -Stage publish

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9]+(?:-[a-z0-9]+)*$')]
    [string]$Project,

    [ValidateSet('setup', 'narration', 'publish')]
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

function Add-Warning([string]$Message) {
    Write-Host "WARN $Message" -ForegroundColor Yellow
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

function Convert-SrtTimestamp([string]$Value) {
    if ($Value -notmatch '^(\d{2}):(\d{2}):(\d{2}),(\d{3})$') {
        throw "Invalid SRT timestamp: $Value"
    }
    return ([int]$Matches[1] * 3600) + ([int]$Matches[2] * 60) +
        [int]$Matches[3] + ([int]$Matches[4] / 1000.0)
}

function Test-Srt([string]$Path, [string]$Label) {
    $lines = Get-Content -LiteralPath $Path -Encoding utf8
    $numbers = @($lines | Where-Object { $_ -match '^\d+$' } | ForEach-Object { [int]$_ })
    $timings = @($lines | Where-Object {
        $_ -match '^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$'
    })

    if ($numbers.Count -eq 0 -or $numbers.Count -ne $timings.Count) {
        Add-Failure "$Label is not a valid numbered SRT ($($numbers.Count) numbers, $($timings.Count) timings)"
        return $null
    }

    for ($index = 0; $index -lt $numbers.Count; $index++) {
        if ($numbers[$index] -ne ($index + 1)) {
            Add-Failure "$Label numbering breaks at entry $($index + 1)"
            return $null
        }
    }

    $previousEnd = -1.0
    $lastEnd = 0.0
    foreach ($timing in $timings) {
        $parts = $timing -split ' --> '
        $start = Convert-SrtTimestamp $parts[0]
        $end = Convert-SrtTimestamp $parts[1]
        if ($end -le $start) {
            Add-Failure "$Label contains a non-positive caption duration: $timing"
            return $null
        }
        if ($start -lt ($previousEnd - 0.001)) {
            Add-Failure "$Label captions overlap or run backwards at: $timing"
            return $null
        }
        $previousEnd = $end
        $lastEnd = $end
    }

    Add-Pass "$Label contains $($numbers.Count) sequential, non-overlapping captions"
    return [pscustomobject]@{
        Count = $numbers.Count
        LastEnd = $lastEnd
    }
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

$schemaVersion = 1
if ($null -ne $manifest.PSObject.Properties['schemaVersion']) {
    $schemaVersion = [int]$manifest.schemaVersion
}

if ($schemaVersion -ge 2) {
    $requiredTtsSettings = @(
        'engine', 'language', 'reference', 'referenceText', 'model',
        'outputDir', 'filenameStem', 'renderMode'
    )
    foreach ($key in $requiredTtsSettings) {
        $property = $manifest.tts.PSObject.Properties[$key]
        if ($null -eq $property -or [string]::IsNullOrWhiteSpace([string]$property.Value)) {
            Add-Failure "project.json tts.$key is required by schema 2"
        }
    }

    if ([string]$manifest.tts.model -notmatch 'Qwen3-TTS-12Hz-1\.7B-Base') {
        Add-Failure 'schema 2 projects must use the standard Qwen3-TTS 1.7B Base model'
    } else {
        Add-Pass 'TTS model uses Qwen3-TTS 1.7B Base'
    }
    if ([string]$manifest.tts.renderMode -ne 'scene') {
        Add-Failure "schema 2 projects must use tts.renderMode 'scene'"
    } else {
        Add-Pass 'TTS render mode is scene-context narration'
    }

    foreach ($key in @('reference', 'referenceText')) {
        $property = $manifest.tts.PSObject.Properties[$key]
        if ($null -ne $property -and -not [string]::IsNullOrWhiteSpace([string]$property.Value)) {
            $privatePath = Resolve-RepoPath ([string]$property.Value)
            if (Test-Path -LiteralPath $privatePath -PathType Leaf) {
                Add-Pass "tts.$key is available locally"
            } else {
                Add-Failure "Missing private TTS input tts.$key -> $($property.Value)"
            }
        }
    }

    if ($null -eq $manifest.PSObject.Properties['audio']) {
        Add-Failure 'schema 2 project.json requires an audio approval section'
    } elseif ($null -eq $manifest.audio.PSObject.Properties['backgroundMusic']) {
        Add-Failure 'schema 2 project.json requires audio.backgroundMusic'
    } else {
        Add-Pass 'audio approval and mix settings are present'
    }
} else {
    Add-Warning 'legacy schema 1 project; the new narration/audio approval rules are not enforced'
}

$setupKeys = @('script', 'sources', 'publishingKo', 'publishingEn', 'motionCanvasProject', 'manimProject')
$resolved = @{}
$scriptLineCount = 0
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
            $scriptLineCount = @(
                $scriptData.scenes | ForEach-Object { @($_.lines).Count }
            ) | Measure-Object -Sum | Select-Object -ExpandProperty Sum
            Add-Pass "narration script contains $scriptLineCount caption lines"
        }
    } catch {
        Add-Failure "Narration script is invalid JSON: $($_.Exception.Message)"
    }
}

$srtKoInfo = $null
$srtEnInfo = $null
$narrationDuration = $null

if ($Stage -in @('narration', 'publish')) {
    foreach ($key in @('narration', 'captionsKo', 'captionsEn')) {
        $resolved[$key] = Test-ManifestFile $manifest.paths $key
    }

    if ($null -ne $resolved.captionsKo) {
        $srtKoInfo = Test-Srt $resolved.captionsKo 'Korean SRT'
    }
    if ($null -ne $resolved.captionsEn) {
        $srtEnInfo = Test-Srt $resolved.captionsEn 'English SRT'
    }
    foreach ($srtInfo in @($srtKoInfo, $srtEnInfo)) {
        if ($null -ne $srtInfo -and $scriptLineCount -gt 0 -and
            $srtInfo.Count -lt $scriptLineCount) {
            Add-Failure "SRT contains only $($srtInfo.Count) captions for $scriptLineCount script lines"
        } elseif ($null -ne $srtInfo -and $srtInfo.Count -gt $scriptLineCount) {
            Add-Pass "SRT expands $scriptLineCount script lines into $($srtInfo.Count) readable caption cues"
        }
    }

    if ($schemaVersion -ge 2) {
        $outputDir = Resolve-RepoPath ([string]$manifest.tts.outputDir)
        $stem = [string]$manifest.tts.filenameStem
        $timingPath = Join-Path $outputDir "$stem.timing.json"
        $asrReviewPath = Join-Path $outputDir "$stem.asr-review.txt"
        if (Test-Path -LiteralPath $timingPath -PathType Leaf) {
            try {
                $timing = Get-Content -LiteralPath $timingPath -Raw -Encoding utf8 | ConvertFrom-Json
                if (@($timing.entries).Count -ne $scriptLineCount) {
                    Add-Failure "timing JSON has $(@($timing.entries).Count) entries; expected $scriptLineCount"
                } elseif ([string]$timing.render_mode -ne 'scene') {
                    Add-Failure "timing JSON render_mode is '$($timing.render_mode)'; expected 'scene'"
                } else {
                    Add-Pass 'timing JSON uses scene rendering and matches the script line count'
                }
            } catch {
                Add-Failure "Invalid narration timing JSON: $($_.Exception.Message)"
            }
        } else {
            Add-Failure "Missing narration timing JSON: $timingPath"
        }

        if (Test-Path -LiteralPath $asrReviewPath -PathType Leaf) {
            Add-Pass 'full-narration ASR review transcript exists'
        } else {
            Add-Failure "Missing full-narration ASR review transcript: $asrReviewPath"
        }
    }

    $ffprobe = Get-Command ffprobe -ErrorAction SilentlyContinue
    if ($null -ne $ffprobe -and $null -ne $resolved.narration) {
        try {
            $narrationDuration = [double](& $ffprobe.Source -v error `
                -show_entries format=duration -of default=nw=1:nk=1 $resolved.narration)
            Add-Pass "narration duration is $([math]::Round($narrationDuration, 2))s"
        } catch {
            Add-Failure "ffprobe could not inspect narration: $($_.Exception.Message)"
        }
    } elseif ($null -eq $ffprobe) {
        Add-Warning 'ffprobe is not installed; media metadata was not checked'
    }
}

if ($Stage -eq 'publish') {
    $resolved['videoClean'] = Test-ManifestFile $manifest.paths 'videoClean'

    if ($schemaVersion -ge 2) {
        $music = $manifest.audio.backgroundMusic
        if ([bool]$music.required -and [string]$music.approvalStatus -ne 'approved') {
            Add-Failure "background music approval is '$($music.approvalStatus)'; expected 'approved'"
        } else {
            Add-Pass 'background music approval gate passed'
        }
        if ([string]$manifest.audio.mixStatus -ne 'final') {
            Add-Failure "audio mix status is '$($manifest.audio.mixStatus)'; expected 'final'"
        } else {
            Add-Pass 'audio mix is marked final'
        }
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

            if ($stream.width -ne [int]$manifest.video.width -or
                $stream.height -ne [int]$manifest.video.height) {
                Add-Failure "video dimensions do not match project.json"
            }
            $audioCodec = & $ffprobe.Source -v error -select_streams a:0 `
                -show_entries stream=codec_name -of default=nw=1:nk=1 $resolved.videoClean
            if ([string]::IsNullOrWhiteSpace([string]$audioCodec)) {
                Add-Failure 'final video has no audio stream'
            } else {
                Add-Pass "final video audio codec is $audioCodec"
            }
            if ($null -ne $narrationDuration -and
                [math]::Abs($duration - $narrationDuration) -gt 0.25) {
                Add-Failure "video and narration durations differ by more than 0.25s"
            }
            if ($null -ne $srtKoInfo -and $srtKoInfo.LastEnd -gt ($duration + 0.05)) {
                Add-Failure 'Korean SRT extends beyond the final video'
            }
        } catch {
            Add-Failure "ffprobe could not inspect the final video: $($_.Exception.Message)"
        }
    } elseif ($null -eq $ffprobe) {
        Add-Warning 'ffprobe is not installed; final media metadata was not checked'
    }
}

Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host "Project check failed with $($failures.Count) issue(s)." -ForegroundColor Red
    exit 1
}

Write-Host "Project '$Project' passed the '$Stage' checks." -ForegroundColor Green
