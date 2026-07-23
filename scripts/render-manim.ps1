# Renders every Manim scene in manim/scenes to shared/output/manim
# Usage: pwsh ./scripts/render-manim.ps1 [-Quality ql|qm|qh|qk]

param(
    [string]$Quality = "qh"
)

Set-Location "$PSScriptRoot/../manim"
Get-ChildItem "scenes" -Filter "*.py" | ForEach-Object {
    manim render "-$Quality" $_.FullName
}
