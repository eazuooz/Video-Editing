$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Resolve-Path "$PSScriptRoot/../../../..")
$data = Get-Content -Raw -Encoding utf8 "$PSScriptRoot/../batch.json" | ConvertFrom-Json
foreach ($row in $data.items | Select-Object -Skip 3) {
    $project = "projects/$($row.slug)"
    $plan = Get-Content -Raw -Encoding utf8 (Join-Path $project 'planning/part2-picture-plan.json') | ConvertFrom-Json
    $queue = Join-Path "$project/production/unity-staging" $plan.preflightQueue
    $s = Split-Path -Parent $queue
    $state = Join-Path $s 'progress.json'
    if (Test-Path $state) {
        $prior = Get-Content -Raw -Encoding utf8 $state | ConvertFrom-Json
        if ($prior.status -eq 'images-ready-for-internal-visual-QA') { continue }
        if (Get-Process -Id $prior.pid -ErrorAction SilentlyContinue) { continue }
    }
    & python -u -X utf8 "$PSScriptRoot/../run-module-preflight.py" --queue "$queue" --run --wait-hours 48
    if ($LASTEXITCODE) { Write-Output "Preview needs inspection: $($row.id)" }
}
