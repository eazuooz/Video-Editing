# Builds and reviews the standard narration package for one video project.
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-project-narration.ps1 `
#     -Project frame-rate-modern-rendering

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9]+(?:-[a-z0-9]+)*$')]
    [string]$Project,

    [switch]$SkipEnglish,
    [switch]$SkipAsr
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$python = Join-Path $repoRoot 'qwen3-tts/.venv/Scripts/python.exe'
$manifestPath = Join-Path $repoRoot "projects/$Project/project.json"

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Qwen3-TTS Python environment not found: $python"
}
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Project manifest not found: $manifestPath"
}

function Resolve-RepoPath([string]$RelativePath) {
    $fullPath = [System.IO.Path]::GetFullPath((Join-Path $repoRoot $RelativePath))
    $rootPrefix = $repoRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar) +
        [System.IO.Path]::DirectorySeparatorChar
    if (-not $fullPath.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Path escapes the repository: $RelativePath"
    }
    return $fullPath
}

function Invoke-PythonTool {
    param(
        [Parameter(Mandatory = $true)][string]$Script,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    $scriptPath = Join-Path $repoRoot $Script
    & $python -X utf8 $scriptPath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Script failed with exit code $LASTEXITCODE"
    }
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json
if ($manifest.slug -ne $Project) {
    throw "Manifest slug '$($manifest.slug)' does not match '$Project'"
}
if ([string]::IsNullOrWhiteSpace([string]$manifest.tts.referenceText)) {
    throw 'project.json tts.referenceText is required by the standard voice-cloning workflow'
}

$referencePath = Resolve-RepoPath ([string]$manifest.tts.reference)
$referenceTextPath = Resolve-RepoPath ([string]$manifest.tts.referenceText)
if (-not (Test-Path -LiteralPath $referencePath -PathType Leaf)) {
    throw "Voice reference not found: $referencePath"
}
if (-not (Test-Path -LiteralPath $referenceTextPath -PathType Leaf)) {
    throw "Voice-reference transcript not found: $referenceTextPath"
}

Write-Host "[1/4] Rendering scene-context narration and Korean captions..."
Invoke-PythonTool -Script 'qwen3-tts/render_narration.py' -Arguments @(
    '--project', $Project,
    '--batch-size', '1'
)

$translationPath = Join-Path $repoRoot "projects/$Project/script/narration.en.json"
if (-not $SkipEnglish -and (Test-Path -LiteralPath $translationPath -PathType Leaf)) {
    Write-Host "[2/4] Building English captions from measured Korean timing..."
    Invoke-PythonTool -Script 'qwen3-tts/build_translated_srt.py' -Arguments @(
        '--project', $Project,
        '--language', 'en'
    )
} else {
    Write-Host '[2/4] English captions skipped.'
}

Write-Host "[3/4] Synchronizing Motion Canvas scene timing and narration asset..."
Invoke-PythonTool -Script 'qwen3-tts/build_project_timing.py' -Arguments @(
    '--project', $Project
)

if (-not $SkipAsr) {
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json
    $outputDir = Resolve-RepoPath ([string]$manifest.tts.outputDir)
    $stem = [string]$manifest.tts.filenameStem
    $narrationPath = Join-Path $outputDir "$stem.wav"
    $reviewPath = Join-Path $outputDir "$stem.asr-review.txt"
    Write-Host "[4/4] Transcribing the complete narration for human review..."
    Invoke-PythonTool -Script 'qwen3-tts/transcribe_reference.py' -Arguments @(
        $narrationPath,
        '--output', $reviewPath
    )
    Write-Host "Review transcript: $reviewPath"
} else {
    Write-Host '[4/4] Full-narration ASR review skipped.'
}

Write-Host ''
Write-Host "Narration package created for '$Project'." -ForegroundColor Green
Write-Host 'Next: review endings, names, numbers, SRT timing, and the ASR transcript.'
Write-Host 'Do not mix background music until the user approves a licensed track.'
