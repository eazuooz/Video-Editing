$ErrorActionPreference = 'Stop'
$script:rootDir = (Resolve-Path "$PSScriptRoot/../../../..").Path
Set-Location -LiteralPath $script:rootDir
$stateDir = Join-Path $PSScriptRoot '../local/part2-20261106'
[IO.Directory]::CreateDirectory($stateDir) | Out-Null
$lock = Join-Path $stateDir 'finite-worker.lock'
# The open handle excludes duplicate invocations; closing it also releases it after a crash.
$owned = [IO.File]::Open($lock,[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::Write,[IO.FileShare]::None)
try {
    while ($true) {
        $raw = & python -X utf8 "$PSScriptRoot/queue_state.py"
        if ($LASTEXITCODE) { throw "Could not read the lesson queue" }
        $scan = $raw | ConvertFrom-Json
        $scan | Add-Member -NotePropertyName checkedAt -NotePropertyValue ([DateTimeOffset]::UtcNow.ToString('o'))
        $scan | Add-Member -NotePropertyName pid -NotePropertyValue $PID
        [IO.File]::WriteAllText((Join-Path $stateDir 'progress.json'), ($scan | ConvertTo-Json -Depth 10))
        if ($scan.candidateBatchDone) { break }
        if (-not $scan.action) { Start-Sleep -Seconds 20; continue }
        $action = $scan.action
        $label = "$($action.episode)-$($action.step)"
        $cmdArgs = @($action.args)
        & $action.exe @cmdArgs *> (Join-Path $stateDir "$label.log")
        $rc=$LASTEXITCODE
        if ($rc -ne 0) {
            [IO.File]::WriteAllText((Join-Path $stateDir "$label-error.json"),(@{exitCode=$rc;episode=$action.episode;stage=$action.step;log="$label.log"} | ConvertTo-Json))
        }
    }
} finally { $owned.Dispose() }
