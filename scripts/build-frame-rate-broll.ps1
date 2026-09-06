param(
    [string]$CacheDir = "",
    [string]$OutputDir = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $repoRoot "qwen3-tts\.venv\Scripts\python.exe"
$defaultOutputDir = Join-Path $repoRoot "motion-canvas\src\projects\frame-rate-modern-rendering\assets\gameplay"

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Python environment not found: $python"
}

if ([string]::IsNullOrWhiteSpace($CacheDir)) {
    $CacheDir = Join-Path ([IO.Path]::GetTempPath()) ("fps-video-" + [guid]::NewGuid().ToString("N"))
}
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = $defaultOutputDir
}

$CacheDir = [IO.Path]::GetFullPath($CacheDir)
$outputDir = [IO.Path]::GetFullPath($OutputDir)
New-Item -ItemType Directory -Force -Path $CacheDir, $outputDir | Out-Null

# Every remote source is pinned by its YouTube video ID. Exact excerpts are
# documented in projects/frame-rate-modern-rendering/sources/SOURCES.md.
$downloads = [ordered]@{
    "HGmyQS09VGQ" = "https://www.youtube.com/watch?v=HGmyQS09VGQ"
    "F2347gyZp0U" = "https://www.youtube.com/watch?v=F2347gyZp0U"
    "myGdMOcdTcE" = "https://www.youtube.com/watch?v=myGdMOcdTcE"
    "d_20X1YM28U" = "https://www.youtube.com/watch?v=d_20X1YM28U"
    "GffelVJeGws" = "https://www.youtube.com/watch?v=GffelVJeGws"
    "lbcYFgQJOLM" = "https://www.youtube.com/watch?v=lbcYFgQJOLM"
    "URBom7N3t6I" = "https://www.youtube.com/watch?v=URBom7N3t6I"
    "LKBctwWbTOk" = "https://www.youtube.com/watch?v=LKBctwWbTOk"
    "iPhESbeKFIE" = "https://www.youtube.com/watch?v=iPhESbeKFIE"
    "jbu294Nv7Q8" = "https://www.youtube.com/watch?v=jbu294Nv7Q8"
    "tiUiCzzVu8g" = "https://www.youtube.com/watch?v=tiUiCzzVu8g"
    "wcn25vlHgec" = "https://www.youtube.com/watch?v=wcn25vlHgec"
    "91kxRGeg9wQ" = "https://www.youtube.com/watch?v=91kxRGeg9wQ"
    "qQn3bsPNTyI" = "https://www.youtube.com/watch?v=qQn3bsPNTyI"
    "avWMEd-H8Qg" = "https://www.youtube.com/watch?v=avWMEd-H8Qg"
    "dR9i2WVcXTM" = "https://www.youtube.com/watch?v=dR9i2WVcXTM"
    "k6YkuhUxETE" = "https://www.youtube.com/watch?v=k6YkuhUxETE"
    "96jRLXyjeao" = "https://www.youtube.com/watch?v=96jRLXyjeao"
}

foreach ($entry in $downloads.GetEnumerator()) {
    $target = Join-Path $CacheDir ($entry.Key + ".mp4")
    if (Test-Path -LiteralPath $target -PathType Leaf) {
        continue
    }

    & $python -m yt_dlp `
        --js-runtimes node `
        -f "bv*[height<=1080]+ba/b[height<=1080]" `
        --merge-output-format mp4 `
        --no-playlist `
        -o $target `
        $entry.Value
    if ($LASTEXITCODE -ne 0) {
        throw "yt-dlp failed: $($entry.Value)"
    }
}

$normalize = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=60,format=yuv420p"

function Invoke-NormalizedClip {
    param(
        [Parameter(Mandatory)] [string]$SourcePath,
        [Parameter(Mandatory)] [double]$Start,
        [Parameter(Mandatory)] [double]$Duration,
        [Parameter(Mandatory)] [string]$Name
    )

    if (-not (Test-Path -LiteralPath $SourcePath -PathType Leaf)) {
        throw "Source video not found: $SourcePath"
    }

    $destination = Join-Path $outputDir $Name
    & ffmpeg -y -loglevel error `
        -ss $Start -t $Duration -i $SourcePath `
        -map 0:v:0 -map 0:a:0? -vf $normalize `
        -c:v libx264 -preset medium -crf 20 -movflags +faststart `
        -c:a aac -b:a 160k -ar 48000 `
        $destination
    if ($LASTEXITCODE -ne 0) {
        throw "ffmpeg failed: $Name"
    }
}

$sf2 = Join-Path $CacheDir "myGdMOcdTcE.mp4"
$mario = Join-Path $CacheDir "HGmyQS09VGQ.mp4"
$streetFighter6 = Join-Path $CacheDir "F2347gyZp0U.mp4"
$forza = Join-Path $CacheDir "d_20X1YM28U.mp4"
$ratchet = Join-Path $CacheDir "GffelVJeGws.mp4"
$overwatchCounter = Join-Path $CacheDir "lbcYFgQJOLM.mp4"
$celeste = Join-Path $CacheDir "URBom7N3t6I.mp4"
$overwatchComparison = Join-Path $CacheDir "LKBctwWbTOk.mp4"
$sonicPalNtsc = Join-Path $CacheDir "iPhESbeKFIE.mp4"
$horizon = Join-Path $CacheDir "jbu294Nv7Q8.mp4"
$alanWake = Join-Path $CacheDir "tiUiCzzVu8g.mp4"
$blackMythAnnouncement = Join-Path $CacheDir "wcn25vlHgec.mp4"
$minecraftRtx = Join-Path $CacheDir "91kxRGeg9wQ.mp4"
$dlssExplainer = Join-Path $CacheDir "qQn3bsPNTyI.mp4"
$cyberpunkFrameGen = Join-Path $CacheDir "avWMEd-H8Qg.mp4"
$starWarsOutlaws = Join-Path $CacheDir "dR9i2WVcXTM.mp4"
$blackMythLaunch = Join-Path $CacheDir "k6YkuhUxETE.mp4"
$counterStrike = Join-Path $CacheDir "96jRLXyjeao.mp4"

Invoke-NormalizedClip $mario 9 6.5 "scene01.mp4"
Invoke-NormalizedClip $streetFighter6 40 6.5 "scene02.mp4"
Invoke-NormalizedClip $sf2 0 6.5 "scene03.mp4"

# One 60fps source sampled at two rates. The 30fps side repeats every second
# frame on a 60fps output timeline; both sides cover the same distance and time.
& ffmpeg -y -loglevel error -ss 250 -t 6.5 -i $forza `
    -filter_complex "[0:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,split=2[a][b];[a]fps=30,crop=640:720:320:0[left];[b]fps=60,crop=640:720:320:0[right];[left][right]hstack=inputs=2,setsar=1,format=yuv420p[out]" `
    -map "[out]" -map 0:a:0? -c:v libx264 -preset medium -crf 20 -movflags +faststart `
    -c:a aac -b:a 160k -ar 48000 `
    (Join-Path $outputDir "scene04.mp4")
if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed: scene04.mp4" }

Invoke-NormalizedClip $ratchet 176 6.5 "scene05.mp4"
Invoke-NormalizedClip $overwatchCounter 14 6.5 "scene06.mp4"
Invoke-NormalizedClip $celeste 90 6.5 "scene07.mp4"
Invoke-NormalizedClip $overwatchComparison 5 6.5 "scene08.mp4"
Invoke-NormalizedClip $sonicPalNtsc 154 6.5 "scene09.mp4"
Invoke-NormalizedClip $horizon 8 6.5 "scene10.mp4"
Invoke-NormalizedClip $alanWake 98 6.5 "scene11.mp4"
Invoke-NormalizedClip $blackMythAnnouncement 14 6.5 "scene12.mp4"
Invoke-NormalizedClip $minecraftRtx 29 6.5 "scene13.mp4"
Invoke-NormalizedClip $dlssExplainer 287 6.5 "scene14.mp4"
Invoke-NormalizedClip $cyberpunkFrameGen 9 6.5 "scene15.mp4"
Invoke-NormalizedClip $starWarsOutlaws 10 6.5 "scene16.mp4"
Invoke-NormalizedClip $blackMythLaunch 14 6.5 "scene17.mp4"
Invoke-NormalizedClip $counterStrike 12 6.5 "scene18.mp4"

# Intentional summary comparison: fixed-timing arcade game versus a modern
# multi-stage rendering workload. Keep both source tracks at a conservative
# level so the final narration-first mix can still use the original sound.
& ffmpeg -y -loglevel error `
    -ss 0 -t 6.5 -i $sf2 `
    -ss 98 -t 6.5 -i $alanWake `
    -filter_complex "[0:v]fps=60,scale=1280:720:force_original_aspect_ratio=increase,crop=640:720:320:0[left];[1:v]fps=60,scale=1280:720:force_original_aspect_ratio=increase,crop=640:720:320:0[right];[left][right]hstack=inputs=2,setsar=1,format=yuv420p[out];[0:a]aresample=48000,volume=0.5[a0];[1:a]aresample=48000,volume=0.5[a1];[a0][a1]amix=inputs=2:duration=shortest:normalize=0,alimiter=limit=0.9[audio]" `
    -map "[out]" -map "[audio]" -c:v libx264 -preset medium -crf 20 -movflags +faststart `
    -c:a aac -b:a 160k -ar 48000 `
    (Join-Path $outputDir "scene19.mp4")
if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed: scene19.mp4" }

# Intentional four-way recap. Each panel comes from a source already explained
# in its own scene, so the repetition has an explicit summary function. The
# four original tracks are blended quietly instead of being discarded.
& ffmpeg -y -loglevel error `
    -ss 40 -t 6.5 -i $streetFighter6 `
    -ss 14 -t 6.5 -i $overwatchCounter `
    -ss 8 -t 6.5 -i $horizon `
    -ss 10 -t 6.5 -i $starWarsOutlaws `
    -filter_complex "[0:v]fps=60,scale=640:360,setsar=1[a];[1:v]fps=60,scale=640:360,setsar=1[b];[2:v]fps=60,scale=640:360,setsar=1[c];[3:v]fps=60,scale=640:360,setsar=1[d];[a][b][c][d]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0,format=yuv420p[out];[0:a]aresample=48000,volume=0.25[a0];[1:a]aresample=48000,volume=0.25[a1];[2:a]aresample=48000,volume=0.25[a2];[3:a]aresample=48000,volume=0.25[a3];[a0][a1][a2][a3]amix=inputs=4:duration=shortest:normalize=0,alimiter=limit=0.9[audio]" `
    -map "[out]" -map "[audio]" -c:v libx264 -preset medium -crf 20 -movflags +faststart `
    -c:a aac -b:a 160k -ar 48000 `
    (Join-Path $outputDir "scene20.mp4")
if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed: scene20.mp4" }

$files = Get-ChildItem -LiteralPath $outputDir -Filter "scene*.mp4" | Sort-Object Name
if ($files.Count -ne 20) {
    throw "Expected 20 scene clips, found $($files.Count)."
}

Write-Host "Created $($files.Count) normalized clips in $outputDir"
Write-Host "Download cache: $CacheDir"
