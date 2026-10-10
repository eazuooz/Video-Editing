param([Parameter(Mandatory=$true)][string]$Destination)
$ErrorActionPreference = 'Stop'
$taskRoot = 'D:\Github\Video-Editing'
$resolvedDestination = [IO.Path]::GetFullPath((Join-Path $taskRoot $Destination))
if (-not $resolvedDestination.StartsWith($taskRoot + '\')) { throw 'Resource record must stay in the project workspace' }
if (Test-Path -LiteralPath $resolvedDestination) { throw 'Preserve existing resource observations; use a fresh path' }
$taskProcesses = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','node.exe','ffmpeg.exe') } | Select-Object ProcessId,ParentProcessId,CreationDate,Name,CommandLine)
$taskHeavy = @($taskProcesses | Where-Object {
    $_.CommandLine -match 'character-parameters' -and (
      $_.Name -eq 'ffmpeg.exe' -or
      $_.CommandLine -match 'review-current-voice-v1.py|review-voice-clarity-v2.py|review-additional-role-action-v2.py|build-measured-native-inputs-v3.py|build-selected-input-preflight-v3.py|build-character-final-mix-v1.py|review-character-mixed-v1.py|render-character-pair-v1.py|extract-character-final-qa-v1.py'
    ) -and $_.CommandLine -notmatch 'capture-current-resource-v6'
})
$clarityPath = Join-Path $taskRoot 'projects/character-parameters/production/voice-clarity-v2/execution.json'
if (Test-Path -LiteralPath $clarityPath) {
    $clarityState = Get-Content -LiteralPath $clarityPath -Raw | ConvertFrom-Json
    if ($null -eq $clarityState.exitCode -and $clarityState.gpuJobs -eq 1) {
      $taskHeavy += @($taskProcesses | Where-Object { $_.ProcessId -eq $clarityState.actualPid })
    }
}
$taskOs = Get-CimInstance Win32_OperatingSystem
$taskCpu = @(Get-CimInstance Win32_Processor | Select-Object -ExpandProperty LoadPercentage)
$taskLeasePath = Join-Path $taskRoot 'shared/output/GPU_HANDOFF.json'
$taskLease = if (Test-Path -LiteralPath $taskLeasePath) { Get-Content -LiteralPath $taskLeasePath -Raw | ConvertFrom-Json } else { $null }
$taskStatus = Get-Content -LiteralPath 'C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json' -Raw | ConvertFrom-Json
$taskRecord = [ordered]@{
    observedAt = [DateTime]::UtcNow.ToString('o')
    ownHeavyJobs = $taskHeavy.Count
    ownHeavyProcesses = $taskHeavy
    cpuLoadPercent = ($taskCpu | Measure-Object -Average).Average
    freePhysicalMemoryKiB = [double]$taskOs.FreePhysicalMemory
    processes = $taskProcesses
    gpu = @(nvidia-smi --query-gpu=timestamp,name,memory.used,memory.free,utilization.gpu --format=csv,noheader)
    currentResearchStatus = $taskStatus
    existingLease = $taskLease
    processMutations = 0
}
$taskRecord | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath $resolvedDestination -Encoding utf8
[ordered]@{ path=$Destination; ownHeavyJobs=$taskHeavy.Count; cpuLoadPercent=$taskRecord.cpuLoadPercent; freePhysicalMemoryKiB=$taskRecord.freePhysicalMemoryKiB; research=$taskStatus.job; leaseState=$taskLease.state } | ConvertTo-Json -Compress
