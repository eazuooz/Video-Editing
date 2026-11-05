$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Resolve-Path "$PSScriptRoot/../../../..")
$data = Get-Content -Raw -Encoding utf8 "$PSScriptRoot/../batch.json" | ConvertFrom-Json
foreach ($row in $data.items | Select-Object -Skip 3) {
    $s = Join-Path "projects/$($row.slug)/production/unity-staging" 'local-preflight-part2-v1'
    $state = Join-Path $s 'progress.json'
    if (Test-Path $state) {
        $prior = Get-Content -Raw -Encoding utf8 $state | ConvertFrom-Json
        if ($prior.status -eq 'images-ready-for-internal-visual-QA') { continue }
        if (Get-Process -Id $prior.pid -ErrorAction SilentlyContinue) { continue }
    }
    & python -u -X utf8 "$PSScriptRoot/../run-module-preflight.py" --queue "$s/queue.json" --run --wait-hours 48
    if ($LASTEXITCODE) { Write-Output "Preview needs inspection: $($row.id)" }
}
