$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$taskRoot = 'D:\Github\Video-Editing'
$taskDest = Join-Path $taskRoot 'projects\limited-color-world\production\resource-before-voice-v2.json'
if (Test-Path -LiteralPath $taskDest) { throw 'Preserve the existing snapshot.' }
$taskProcesses = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|ffmpeg|ffprobe|node' } | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine)
$taskOwn = @($taskProcesses | Where-Object { $_.CommandLine -match 'limited-color-world' -and $_.CommandLine -notmatch 'capture-resource|verify-failed' })
$taskLeasePath = Join-Path $taskRoot 'shared\output\GPU_HANDOFF.json'
$taskLease = if (Test-Path -LiteralPath $taskLeasePath) { Get-Content -LiteralPath $taskLeasePath -Raw | ConvertFrom-Json } else { $null }
$taskQueue = Get-Content -LiteralPath 'C:\Users\eazuo\renderformer\tmp\placement_focus_20261008\status.json' -Raw | ConvertFrom-Json
$taskControls = @('C:\Users\eazuo\renderformer\tmp\placement_focus_20261008\STOP','C:\Users\eazuo\renderformer\GPU_PAUSE','C:\Users\eazuo\renderformer\tools\logs\GPU_PAUSE') | ForEach-Object {
    [pscustomobject]@{path=$_;exists=(Test-Path -LiteralPath $_);content=$(if(Test-Path -LiteralPath $_){Get-Content -LiteralPath $_ -Raw}else{$null})}
}
$taskOs = Get-CimInstance Win32_OperatingSystem
$taskCpu = Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average
$taskGpu = (& nvidia-smi --query-gpu=name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits | Out-String).Trim()
$taskGpuApps = (& nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader,nounits | Out-String).Trim()
$taskSnapshot = [ordered]@{observedAt=(Get-Date).ToUniversalTime().ToString('o');processes=$taskProcesses;ownHeavyJobs=$taskOwn.Count;ownProcesses=$taskOwn;cpuLoadPercent=$taskCpu.Average;freePhysicalMemoryKiB=$taskOs.FreePhysicalMemory;gpu=$taskGpu;gpuApps=$taskGpuApps;foreignLease=$taskLease;researchQueue=$taskQueue;cooperativeControls=$taskControls;researchManipulatedBySnapshot=$false;ownFailedRequestRestorationVerification='projects/limited-color-world/production/failed-request-research-resume-verification-v1.json'}
$taskSnapshot | ConvertTo-Json -Depth 18 | Set-Content -LiteralPath $taskDest -Encoding utf8
[pscustomobject]@{observedAt=$taskSnapshot.observedAt;ownHeavyJobs=$taskOwn.Count;cpuLoadPercent=$taskCpu.Average;freePhysicalMemoryKiB=$taskOs.FreePhysicalMemory;gpu=$taskGpu;lease=$taskLease;researchQueue=$taskQueue} | ConvertTo-Json -Depth 8
