# Creates the editorial folder and starter projects for both render engines.
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/new-video-project.ps1 -Slug "camera-shake" `
#     -TitleKo "카메라 흔들림은 어떻게 손맛을 만들까?" `
#     -TitleEn "How Does Camera Shake Create Impact?"

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9]+(?:-[a-z0-9]+)*$')]
    [string]$Slug,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$TitleKo,

    [string]$TitleEn = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$projectTemplate = Join-Path $repoRoot "templates/video-project"
$motionTemplate = Join-Path $repoRoot "templates/motion-canvas-project"
$manimTemplate = Join-Path $repoRoot "templates/manim-project"

$projectTarget = Join-Path $repoRoot "projects/$Slug"
$motionTarget = Join-Path $repoRoot "motion-canvas/src/projects/$Slug"
$manimTarget = Join-Path $repoRoot "manim/projects/$Slug"
$registryPath = Join-Path $repoRoot "motion-canvas/projects.json"

foreach ($template in @($projectTemplate, $motionTemplate, $manimTemplate)) {
    if (-not (Test-Path -LiteralPath $template -PathType Container)) {
        throw "Template directory not found: $template"
    }
}

foreach ($target in @($projectTarget, $motionTarget, $manimTarget)) {
    if (Test-Path -LiteralPath $target) {
        throw "Target already exists: $target"
    }
}

if ([string]::IsNullOrWhiteSpace($TitleEn)) {
    $TitleEn = $TitleKo
}

function Copy-TemplateDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    New-Item -ItemType Directory -Path $Destination | Out-Null
    Get-ChildItem -LiteralPath $Source -Force |
        Copy-Item -Destination $Destination -Recurse -Force
}

Copy-TemplateDirectory -Source $projectTemplate -Destination $projectTarget
Copy-TemplateDirectory -Source $motionTemplate -Destination $motionTarget
Copy-TemplateDirectory -Source $manimTemplate -Destination $manimTarget

$tokens = [ordered]@{
    '{{SLUG}}' = $Slug
    '{{TITLE_KO}}' = $TitleKo
    '{{TITLE_EN}}' = $TitleEn
    '{{CREATED_AT}}' = (Get-Date -Format 'yyyy-MM-dd')
}
$textExtensions = @('.md', '.json', '.csv', '.ts', '.tsx', '.py')
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)

foreach ($target in @($projectTarget, $motionTarget, $manimTarget)) {
    Get-ChildItem -LiteralPath $target -Recurse -File | Where-Object {
        $textExtensions -contains $_.Extension.ToLowerInvariant()
    } | ForEach-Object {
        $content = [System.IO.File]::ReadAllText($_.FullName)
        foreach ($token in $tokens.Keys) {
            $content = $content.Replace($token, $tokens[$token])
        }
        [System.IO.File]::WriteAllText($_.FullName, $content, $utf8NoBom)
    }
}

if (-not (Test-Path -LiteralPath $registryPath -PathType Leaf)) {
    throw "Motion Canvas project registry not found: $registryPath"
}

$parsedRegistry = Get-Content -LiteralPath $registryPath -Raw -Encoding utf8 | ConvertFrom-Json
$registeredProjects = @()
foreach ($registeredProject in $parsedRegistry) {
    $registeredProjects += [string]$registeredProject
}
$motionEntry = "./src/projects/$Slug/project.ts"
if ($registeredProjects -notcontains $motionEntry) {
    $registeredProjects += $motionEntry
    # Windows PowerShell 5 can serialize an expanded array as an object with
    # Value/Count properties when it is passed to ConvertTo-Json as one input.
    # Encode each string separately so projects.json is always a plain JSON
    # string array on both Windows PowerShell and PowerShell 7.
    $encodedProjects = @(
        $registeredProjects | ForEach-Object {
            ConvertTo-Json -InputObject ([string]$_) -Compress
        }
    )
    $registryJson = "[" + [Environment]::NewLine +
        "  " + ($encodedProjects -join ("," + [Environment]::NewLine + "  ")) +
        [Environment]::NewLine + "]"
    [System.IO.File]::WriteAllText($registryPath, $registryJson + [Environment]::NewLine, $utf8NoBom)
}

Write-Host "Created video project '$Slug'."
Write-Host "  Editorial:     $projectTarget"
Write-Host "  Motion Canvas: $motionTarget"
Write-Host "  Manim:         $manimTarget"
Write-Host ""
Write-Host "Next: edit projects/$Slug/planning/outline.md and script/narration.ko.json"
Write-Host "Open Motion Canvas with: npm start"
Write-Host "Render Manim with: powershell -NoProfile -ExecutionPolicy Bypass -File scripts/render-manim.ps1 -Project $Slug"
