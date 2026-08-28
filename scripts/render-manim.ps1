# Renders either a named project's Manim file or every legacy scene.
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/render-manim.ps1 -Project camera-shake
#   powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/render-manim.ps1 -Quality ql

param(
    [ValidateSet("ql", "qm", "qh", "qk")]
    [string]$Quality = "qh",
    [ValidatePattern('^[a-z0-9]+(?:-[a-z0-9]+)*$')]
    [string]$Project = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$manimRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "../manim"))
Set-Location $manimRoot

if (-not [string]::IsNullOrWhiteSpace($Project)) {
    $sceneFile = Join-Path $manimRoot "projects/$Project/scene.py"
    if (-not (Test-Path -LiteralPath $sceneFile -PathType Leaf)) {
        throw "Manim project not found: $sceneFile"
    }

    $mediaDir = Join-Path $manimRoot "../shared/output/manim/$Project"
    manim render "-$Quality" --media_dir $mediaDir $sceneFile
    exit $LASTEXITCODE
}

Get-ChildItem -LiteralPath (Join-Path $manimRoot "scenes") -Filter "*.py" | ForEach-Object {
    manim render "-$Quality" $_.FullName
}
