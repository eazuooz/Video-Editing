param([Parameter(Mandatory=$true)][ValidateSet('contexts','targets','extra-native','prototype')][string]$Step,[ValidateRange(1,99)][int]$Version=1)
$ErrorActionPreference='Stop'
$taskRoot='D:\Github\Video-Editing'
$taskDest=Join-Path $taskRoot ('projects\limited-color-world\production\resource-before-'+$Step+'-v'+$Version+'.json')
if(Test-Path -LiteralPath $taskDest){throw 'Preserve existing resource snapshot.'}
$taskProcesses=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match 'python|ffmpeg|ffprobe|node'} | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine)
$taskOwn=@($taskProcesses | Where-Object {$_.CommandLine -match 'limited-color-world' -and $_.CommandLine -match 'render-voice|review-current-voice|extract-|render-|ffmpeg|ffprobe'})
$taskOs=Get-CimInstance Win32_OperatingSystem
$taskCpu=(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
$taskGpu=(& nvidia-smi --query-gpu=name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits | Out-String).Trim()
$taskLeasePath=Join-Path $taskRoot 'shared\output\GPU_HANDOFF.json'
$taskLease=if(Test-Path -LiteralPath $taskLeasePath){Get-Content -LiteralPath $taskLeasePath -Raw | ConvertFrom-Json}else{$null}
$taskQueue=Get-Content -LiteralPath 'C:\Users\eazuo\renderformer\tmp\placement_focus_20261008\status.json' -Raw | ConvertFrom-Json
$taskSnap=[ordered]@{observedAt=(Get-Date).ToUniversalTime().ToString('o');step=$Step;processes=$taskProcesses;ownHeavyJobs=$taskOwn.Count;ownProcesses=$taskOwn;cpuLoadPercent=$taskCpu;freePhysicalMemoryKiB=$taskOs.FreePhysicalMemory;gpu=$taskGpu;foreignLease=$taskLease;researchQueue=$taskQueue;researchManipulatedBySnapshot=$false}
$taskSnap | ConvertTo-Json -Depth 18 | Set-Content -LiteralPath $taskDest -Encoding utf8
[pscustomobject]@{observedAt=$taskSnap.observedAt;ownHeavyJobs=$taskOwn.Count;cpuLoadPercent=$taskCpu;freePhysicalMemoryKiB=$taskOs.FreePhysicalMemory;gpu=$taskGpu;researchQueue=$taskQueue} | ConvertTo-Json -Depth 8
