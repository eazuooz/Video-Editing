# Concatenates rendered clips from both editors into one final video.
# List the clips in the order you want them to play, then run:
#   pwsh ./scripts/combine.ps1 -Clips "shared/output/manim/.../Example.mp4","shared/output/motion-canvas/.../project.mp4"
# Requires ffmpeg on PATH.

param(
    [Parameter(Mandatory = $true)]
    [string[]]$Clips,
    [string]$Out = "shared/output/final.mp4"
)

$root = "$PSScriptRoot/.."
$listFile = New-TemporaryFile
$Clips | ForEach-Object {
    "file '$(Resolve-Path (Join-Path $root $_))'" | Add-Content $listFile
}

ffmpeg -f concat -safe 0 -i $listFile -c copy (Join-Path $root $Out)
Remove-Item $listFile
