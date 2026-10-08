param([Parameter(Mandatory=$true)][string]$Evidence)
$ErrorActionPreference='Stop'
$procs=@(Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,CreationDate,ExecutablePath,CommandLine)
$own=@($procs | Where-Object { $_.CommandLine -match 'player-customization' -and $_.Name -match '^(python(?:w)?|ffmpeg|ffprobe)\.exe$' })
$os=Get-CimInstance Win32_OperatingSystem
$gpu=@(& nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits)
$record=[ordered]@{schemaVersion=1;observedAt=[DateTime]::UtcNow.ToString('o');cpuLoadPercent=(Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average;freePhysicalMemoryKiB=$os.FreePhysicalMemory;ownHeavyJobs=$own.Count;ownHeavyProcesses=$own;gpu=$gpu;relevantProcesses=@($procs | Where-Object { $_.Name -match '^(python|ffmpeg|node)' -and ($_.CommandLine -match 'player-customization|renderformer|gpu_queue|phase1|train_multiview|YamYam|train_v2|pythonw') });foreignProcessesTerminated=0}
$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Evidence -Encoding utf8
[ordered]@{observedAt=$record.observedAt;cpuLoadPercent=$record.cpuLoadPercent;freePhysicalMemoryKiB=$record.freePhysicalMemoryKiB;ownHeavyJobs=$record.ownHeavyJobs;gpu=$gpu;own=$own} | ConvertTo-Json -Depth 5 -Compress
