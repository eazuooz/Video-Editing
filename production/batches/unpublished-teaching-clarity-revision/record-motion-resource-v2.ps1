param([Parameter(Mandatory=$true)][string]$OutputName)
$ErrorActionPreference='Stop'
if($OutputName -notmatch '^[a-z0-9-]+\.json$'){throw 'Exact local resource filename required'}
$motionProcesses=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match 'python|ffmpeg|node' -and $_.CommandLine -match 'Video-Editing|renderformer|qwen' -and $_.CommandLine -notmatch 'trusted-worker|kernel\.js| --eval '} | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine)
$motionCpu=@(Get-CimInstance Win32_Processor | Select-Object -ExpandProperty LoadPercentage)
$motionOs=Get-CimInstance Win32_OperatingSystem
$motionOwn=@($motionProcesses|Where-Object {$_.CommandLine -match 'render-motion-two-targets|render-motion-aim-target|assemble-motion-current-pair|extract-motion-current-final-pixels|review-motion-two-targets|review-motion-aim-target'})
$motionResource=[ordered]@{observedAt=[DateTime]::UtcNow.ToString('o');cpuLoadPercent=($motionCpu|Measure-Object -Average).Average;freePhysicalMemoryKiB=$motionOs.FreePhysicalMemory;ownHeavyCpuJobs=$motionOwn.Count;processes=$motionProcesses;gpuProcesses=(& nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader|Out-String);gpu=(& nvidia-smi --query-gpu=name,memory.used,utilization.gpu --format=csv,noheader|Out-String);researchManipulations=0}
$motionResource | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path 'projects/motion-sickness-games/production/revision-teaching-clarity-v1' $OutputName) -Encoding UTF8
[pscustomobject]$motionResource|Select-Object observedAt,cpuLoadPercent,freePhysicalMemoryKiB,ownHeavyCpuJobs,gpu|ConvertTo-Json
