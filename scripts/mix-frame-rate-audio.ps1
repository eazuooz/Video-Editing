[CmdletBinding()]
param(
    [ValidatePattern('^[a-z0-9]+(?:-[a-z0-9]+)*$')]
    [string]$Project = 'frame-rate-modern-rendering',

    [string]$VideoPath = '',

    [string]$MusicPath = '',

    [string]$OutputPath = '',

    [switch]$ExportBackgroundReview
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$manifestPath = Join-Path $repoRoot "projects/$Project/project.json"
$ffmpeg = (Get-Command ffmpeg -ErrorAction Stop).Source
$ffprobe = (Get-Command ffprobe -ErrorAction Stop).Source

function Resolve-RepoPath {
    param(
        [Parameter(Mandatory)] [string]$Path,
        [switch]$AllowMissing
    )

    $candidate = if ([IO.Path]::IsPathRooted($Path)) {
        [IO.Path]::GetFullPath($Path)
    } else {
        [IO.Path]::GetFullPath((Join-Path $repoRoot $Path))
    }

    $rootPrefix = $repoRoot.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    if (-not $candidate.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path escapes the repository: $Path"
    }
    if (-not $AllowMissing -and -not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
        throw "File not found: $candidate"
    }
    return $candidate
}

function Format-Number([double]$Value) {
    return $Value.ToString('0.###', [Globalization.CultureInfo]::InvariantCulture)
}

function Test-AudioStream([string]$Path) {
    $codec = & $ffprobe -v error -select_streams a:0 `
        -show_entries stream=codec_name -of default=nw=1:nk=1 $Path
    return -not [string]::IsNullOrWhiteSpace([string]$codec)
}

if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Project manifest not found: $manifestPath"
}

$manifest = Get-Content -Raw -Encoding utf8 -LiteralPath $manifestPath | ConvertFrom-Json
$video = if ([string]::IsNullOrWhiteSpace($VideoPath)) {
    Resolve-RepoPath ([string]$manifest.paths.videoClean)
} else {
    Resolve-RepoPath $VideoPath
}
$narration = Resolve-RepoPath ([string]$manifest.paths.narration)
$previewProperty = $manifest.paths.PSObject.Properties['audioMix']
$preview = if ($null -ne $previewProperty) {
    Resolve-RepoPath ([string]$previewProperty.Value) -AllowMissing
} else {
    Resolve-RepoPath "motion-canvas/src/projects/$Project/assets/final-mix.m4a" -AllowMissing
}

if ([string]::IsNullOrWhiteSpace($MusicPath)) {
    $musicProperty = $manifest.audio.backgroundMusic.PSObject.Properties['file']
    if ($null -eq $musicProperty -or [string]::IsNullOrWhiteSpace([string]$musicProperty.Value)) {
        throw 'MusicPath is empty and project.json audio.backgroundMusic.file is not set.'
    }
    $music = Resolve-RepoPath ([string]$musicProperty.Value)
} else {
    $music = Resolve-RepoPath $MusicPath
}

$output = if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $video
} else {
    Resolve-RepoPath $OutputPath -AllowMissing
}

$timingDir = Resolve-RepoPath -Path ([string]$manifest.tts.outputDir) -AllowMissing
$timingPath = Join-Path $timingDir (([string]$manifest.tts.filenameStem) + '.timing.json')
if (-not (Test-Path -LiteralPath $timingPath -PathType Leaf)) {
    throw "Narration timing file not found: $timingPath"
}

$timing = Get-Content -Raw -Encoding utf8 -LiteralPath $timingPath | ConvertFrom-Json
$groups = @($timing.entries | Group-Object scene_id | Sort-Object { [int]$_.Name })
if ($groups.Count -ne 20) {
    throw "Expected 20 narration scenes, found $($groups.Count)."
}

$videoDuration = [double](& $ffprobe -v error -show_entries format=duration `
    -of default=nw=1:nk=1 $video)
$sceneWindows = [System.Collections.Generic.List[object]]::new()
for ($index = 0; $index -lt $groups.Count; $index++) {
    $start = [double](($groups[$index].Group | Measure-Object start -Minimum).Minimum)
    $end = if ($index -lt ($groups.Count - 1)) {
        [double](($groups[$index + 1].Group | Measure-Object start -Minimum).Minimum)
    } else {
        $videoDuration
    }
    # Match build_project_timing.py's 30fps scene boundary grid.
    $start = [math]::Round($start * 30) / 30
    if ($index -lt ($groups.Count - 1)) { $end = [math]::Round($end * 30) / 30 }
    $sceneWindows.Add([pscustomobject]@{
        Id = $groups[$index].Name.PadLeft(2, '0')
        Start = $start
        End = $end
    })
}

$gameplayDir = Join-Path $repoRoot "motion-canvas/src/projects/$Project/assets/gameplay"
$musicFallbackScenes = @($manifest.audio.musicFallbackScenes)
$gameInputs = [System.Collections.Generic.List[object]]::new()
$ffmpegArgs = [System.Collections.Generic.List[string]]::new()
foreach ($argument in @('-y', '-hide_banner', '-loglevel', 'warning', '-i', $video, '-i', $narration,
        '-i', $music)) {
    $ffmpegArgs.Add($argument)
}

$nextInput = 3
foreach ($scene in $sceneWindows) {
    $clip = Join-Path $gameplayDir ("scene{0}.mp4" -f $scene.Id)
    if (-not (Test-Path -LiteralPath $clip -PathType Leaf)) {
        throw "Missing gameplay clip: $clip"
    }
    if ($scene.Id -in $musicFallbackScenes -or -not (Test-AudioStream $clip)) {
        if ($scene.Id -notin $musicFallbackScenes) { $musicFallbackScenes += $scene.Id }
        continue
    }

    $ffmpegArgs.Add('-i')
    $ffmpegArgs.Add($clip)
    $gameInputs.Add([pscustomobject]@{
        Scene = $scene
        Input = $nextInput
    })
    $nextInput++
}

$narrationTarget = Format-Number ([double]$manifest.audio.narrationTargetLufs)
$truePeak = Format-Number ([double]$manifest.audio.truePeakDbtp)
$gameTargetProperty = $manifest.audio.PSObject.Properties['gameAudioTargetLufs']
$musicTargetProperty = $manifest.audio.PSObject.Properties['bgmTargetLufs']
$duckingThresholdProperty = $manifest.audio.PSObject.Properties['duckingThreshold']
$duckingRatioProperty = $manifest.audio.PSObject.Properties['duckingRatio']
$gameTarget = Format-Number $(if ($null -eq $gameTargetProperty) { -23.0 } else { [double]$gameTargetProperty.Value })
$musicTarget = Format-Number $(if ($null -eq $musicTargetProperty) { -28.0 } else { [double]$musicTargetProperty.Value })
$duckingThreshold = Format-Number $(if ($null -eq $duckingThresholdProperty) { 0.08 } else { [double]$duckingThresholdProperty.Value })
$duckingRatio = Format-Number $(if ($null -eq $duckingRatioProperty) { 2.2 } else { [double]$duckingRatioProperty.Value })
$overlapProperty = $manifest.audio.PSObject.Properties['bgmDuringGameplayDb']
$overlapDb = if ($null -eq $overlapProperty) { -3.0 } else { [double]$overlapProperty.Value }
if ($overlapDb -gt 0 -or $overlapDb -lt -12) { throw 'bgmDuringGameplayDb must be between -12 and 0 dB.' }
$placementProperty = $manifest.audio.PSObject.Properties['bgmPlacement']
if ($null -ne $placementProperty -and [string]$placementProperty.Value -ne 'continuous') {
    throw 'This mixer uses bgmPlacement=continuous.'
}
$musicDuration = [double](& $ffprobe -v error -show_entries format=duration `
    -of default=nw=1:nk=1 $music)
if ($musicDuration -le 1) { throw 'Background music must be longer than one second.' }
$loopProperty = $manifest.audio.PSObject.Properties['bgmLoopCrossfadeSeconds']
$loopFade = if ($null -eq $loopProperty) { 1.0 } else { [double]$loopProperty.Value }
if ($loopFade -le 0 -or $loopFade -gt ($musicDuration / 2)) {
    throw 'bgmLoopCrossfadeSeconds must be positive and at most half the music duration.'
}
$musicCopies = [math]::Max(1, [int][math]::Ceiling(($videoDuration - $loopFade) / ($musicDuration - $loopFade)))
$filters = [System.Collections.Generic.List[string]]::new()
$filters.Add("[1:a:0]aresample=48000,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,loudnorm=I=${narrationTarget}:TP=${truePeak}:LRA=7,aresample=48000,asplit=2[narration_mix][narration_key]")

# One continuous song timeline, with a short crossfade only when the song loops.
# Do not restart or fade the music to silence at scene/B-roll boundaries.
$filters.Add('[2:a:0]asetpts=PTS-STARTPTS,aresample=48000,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[music_source]')
$musicTimeline = 'music_source'
if ($musicCopies -gt 1) {
    $copyLabels = @(0..($musicCopies - 1) | ForEach-Object { "music_copy$_" })
    $copyOutputs = ($copyLabels | ForEach-Object { "[$_]" }) -join ''
    $filters.Add("[music_source]asplit=${musicCopies}${copyOutputs}")
    $musicTimeline = $copyLabels[0]
    for ($index = 1; $index -lt $musicCopies; $index++) {
        $joined = "music_loop$index"
        $filters.Add("[$musicTimeline][$($copyLabels[$index])]acrossfade=d=$(Format-Number $loopFade):c1=tri:c2=tri[$joined]")
        $musicTimeline = $joined
    }
}

# Smoothly lower, but never switch off, music while usable source audio plays.
$activity = @($gameInputs | ForEach-Object {
    $start = Format-Number $_.Scene.Start
    $end = Format-Number ([math]::Min($_.Scene.End, $_.Scene.Start + 6.5))
    "min(max((t-$start)/0.45,0),1)*min(max(($end-t)/0.45,0),1)"
})
$gain = Format-Number ([math]::Pow(10, $overlapDb / 20))
$volumeExpression = if ($activity.Count -gt 0) {
    "1-(1-$gain)*min(1,$($activity -join '+'))"
} else { '1' }
$musicFadeOut = Format-Number ([math]::Max(0, $videoDuration - 0.45))
$filters.Add("[$musicTimeline]atrim=duration=$(Format-Number $videoDuration),asetpts=PTS-STARTPTS,loudnorm=I=${musicTarget}:TP=-8:LRA=8,aresample=48000,volume='$volumeExpression':eval=frame,afade=t=in:st=0:d=0.45,afade=t=out:st=${musicFadeOut}:d=0.45[bgm_continuous]")
if ($ExportBackgroundReview) {
    $filters.Add('[bgm_continuous]asplit=2[bgm_bed][bgm_review]')
} else {
    $filters.Add('[bgm_continuous]anull[bgm_bed]')
}
$bedLabels = [System.Collections.Generic.List[string]]::new()
$bedLabels.Add('bgm_bed')

foreach ($gameInput in $gameInputs) {
    $scene = $gameInput.Scene
    $delayMs = [math]::Round($scene.Start * 1000)
    $gameLength = [math]::Min(6.5, $scene.End - $scene.Start)
    $fadeOutStart = [math]::Max(0.0, $gameLength - 0.3)
    $label = "game$($scene.Id)"
    $filters.Add("[$($gameInput.Input):a:0]atrim=start=0:end=$(Format-Number $gameLength),asetpts=PTS-STARTPTS,aresample=48000,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,loudnorm=I=${gameTarget}:TP=-6:LRA=10,afade=t=in:st=0:d=0.12,afade=t=out:st=$(Format-Number $fadeOutStart):d=0.3,adelay=delays=${delayMs}:all=1[$label]")
    $bedLabels.Add($label)
}

if ($bedLabels.Count -eq 0) {
    throw 'No background music or source-audio tracks were prepared.'
}

$bedInputs = ($bedLabels | ForEach-Object { "[$_]" }) -join ''
$filters.Add("${bedInputs}amix=inputs=$($bedLabels.Count):duration=longest:dropout_transition=0:normalize=0[bed]")
$filters.Add("[bed][narration_key]sidechaincompress=threshold=${duckingThreshold}:ratio=${duckingRatio}:attack=15:release=280:makeup=1[bed_ducked]")
if ($ExportBackgroundReview) {
    $filters.Add('[bed_ducked]asplit=2[bed_for_mix][bed_review]')
} else {
    $filters.Add('[bed_ducked]anull[bed_for_mix]')
}
$filters.Add("[narration_mix][bed_for_mix]amix=inputs=2:weights='1 1':normalize=0:duration=longest,alimiter=limit=0.79:attack=5:release=100:level=0,apad=whole_dur=$(Format-Number $videoDuration)[final_audio]")

$filterGraph = $filters -join ";`n"
$renderTarget = Join-Path ([IO.Path]::GetDirectoryName($output)) `
    ('.' + [IO.Path]::GetFileNameWithoutExtension($output) + '.mixing-' + [guid]::NewGuid().ToString('N') + '.mp4')
$previewTarget = Join-Path ([IO.Path]::GetDirectoryName($preview)) `
    ('.final-mix-' + [guid]::NewGuid().ToString('N') + '.m4a')

New-Item -ItemType Directory -Force -Path ([IO.Path]::GetDirectoryName($renderTarget)) | Out-Null
foreach ($argument in @(
        '-filter_complex', $filterGraph,
        '-map', '0:v:0', '-map', '[final_audio]',
        '-map_metadata', '0', '-c:v', 'copy',
        '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2',
        '-t', (Format-Number $videoDuration), '-movflags', '+faststart',
        '-metadata', 'comment=Narration + original source audio + YouTube Audio Library BGM',
        $renderTarget
    )) {
    $ffmpegArgs.Add($argument)
}

if ($ExportBackgroundReview) {
    $reviewDir = Join-Path $repoRoot "shared/output/motion-canvas/$Project-qa"
    New-Item -ItemType Directory -Force -Path $reviewDir | Out-Null
    $reviewPath = Join-Path $reviewDir 'background-only.wav'
    foreach ($argument in @('-map', '[bed_review]', '-c:a', 'pcm_s16le', '-ar', '48000',
            '-ac', '2', '-t', (Format-Number $videoDuration), $reviewPath)) {
        $ffmpegArgs.Add($argument)
    }
    $musicReviewPath = Join-Path $reviewDir 'bgm-only-before-narration-ducking.wav'
    foreach ($argument in @('-map', '[bgm_review]', '-c:a', 'pcm_s16le', '-ar', '48000',
            '-ac', '2', '-t', (Format-Number $videoDuration), $musicReviewPath)) {
        $ffmpegArgs.Add($argument)
    }
}

Write-Host "Mixing $($gameInputs.Count) source-audio scene(s) over continuous BGM ($musicCopies song pass(es))..."
try {
    & $ffmpeg @ffmpegArgs
    if ($LASTEXITCODE -ne 0) {
        throw "ffmpeg exited with code $LASTEXITCODE"
    }

    $probeJson = & $ffprobe -v error -show_entries `
        format=duration:stream=index,codec_type,codec_name,sample_rate,channels `
        -of json $renderTarget
    $probe = $probeJson | ConvertFrom-Json
    $audio = @($probe.streams | Where-Object codec_type -eq 'audio')
    $renderedDuration = [double]$probe.format.duration
    if ($audio.Count -ne 1 -or [math]::Abs($renderedDuration - $videoDuration) -gt 0.25) {
        throw 'Rendered mix failed stream or duration validation.'
    }

    # The editor and its FFmpeg exporter must use the same audio as this MP4.
    # Copy AAC packets, not the narration-only WAV or another lossy encode.
    New-Item -ItemType Directory -Force -Path ([IO.Path]::GetDirectoryName($preview)) | Out-Null
    & $ffmpeg -y -hide_banner -loglevel error -i $renderTarget -map 0:a:0 -vn `
        -c:a copy -movflags +faststart $previewTarget
    if ($LASTEXITCODE -ne 0 -or -not (Test-AudioStream $previewTarget)) {
        throw 'Could not create the mixed-audio asset for Motion Canvas.'
    }
    Move-Item -Force -LiteralPath $renderTarget -Destination $output
    Move-Item -Force -LiteralPath $previewTarget -Destination $preview
} catch {
    foreach ($temporaryFile in @($renderTarget, $previewTarget)) {
        if (Test-Path -LiteralPath $temporaryFile -PathType Leaf) {
            Remove-Item -Force -LiteralPath $temporaryFile
        }
    }
    throw
}

Write-Host "Final mix: $output"
Write-Host "Motion Canvas audio: $preview"
Write-Host "Source-audio scenes: $($gameInputs.Scene.Id -join ', ')"
Write-Host "Music fallback scenes: $($musicFallbackScenes -join ', ')"
Write-Host "BGM: continuous, $overlapDb dB during source audio, ${loopFade}s loop crossfade"
