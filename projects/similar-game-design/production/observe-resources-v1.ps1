param([Parameter(Mandatory=$true)][string]$Evidence)
$ErrorActionPreference='Stop'
$similarProcesses=@(Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,CreationDate,ExecutablePath,CommandLine)
$similarOwn=@($similarProcesses | Where-Object { $_.CommandLine -match 'similar-game-design' -and $_.Name -match '^(python(?:w)?|ffmpeg|ffprobe)\.exe$' })
$similarOs=Get-CimInstance Win32_OperatingSystem
$similarGpu=@(& nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits)
$similarRecord=[ordered]@{schemaVersion=1;observedAt=[DateTime]::UtcNow.ToString('o');cpuLoadPercent=(Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average;freePhysicalMemoryKiB=$similarOs.FreePhysicalMemory;ownHeavyJobs=$similarOwn.Count;ownHeavyProcesses=$similarOwn;gpu=$similarGpu;relevantProcesses=@($similarProcesses | Where-Object { $_.Name -match '^(python|ffmpeg|node)' -and ($_.CommandLine -match 'similar-game-design|renderformer|gpu_queue|phase1|train_multiview|YamYam|train_v2|pythonw|gpu-handoff') });foreignProcessesTerminated=0}
$similarRecord | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Evidence -Encoding utf8
[pscustomobject]@{observedAt=$similarRecord.observedAt;cpuLoadPercent=$similarRecord.cpuLoadPercent;freePhysicalMemoryKiB=$similarRecord.freePhysicalMemoryKiB;ownHeavyJobs=$similarRecord.ownHeavyJobs;gpu=$similarGpu;own=$similarOwn} | ConvertTo-Json -Depth 5 -Compress
