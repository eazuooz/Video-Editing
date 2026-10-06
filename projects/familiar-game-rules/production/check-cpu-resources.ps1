param([Parameter(Mandatory=$true)][string]$Output)
$ErrorActionPreference='Stop'
$root=(Resolve-Path -LiteralPath 'D:\Github\Video-Editing').Path
$target=[IO.Path]::GetFullPath((Join-Path $root $Output))
if (-not $target.StartsWith($root+[IO.Path]::DirectorySeparatorChar)) {throw 'Resource output outside workspace'}
$processes=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|ffmpeg|node' } | Select-Object ProcessId,ParentProcessId,CreationDate,Name,CommandLine)
$heavy=@($processes | Where-Object { $_.CommandLine -match 'familiar-game-rules' -and $_.CommandLine -match 'build-final-mix|build-framed-visual|review-final-mix|render-reviewed-pair|extract-encoded-caption|extract-encoded-final' })
$cpu=(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
$gpu=@(& nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv,noheader)
$record=[ordered]@{ observedAt=[DateTimeOffset]::UtcNow.ToString('o');cpuLoadPercent=$cpu;ownHeavyJobs=$heavy.Count;ownHeavyProcesses=$heavy;allRelevantProcesses=$processes;gpu=$gpu;gpuJobsStarted=0;foreignProcessesPreserved=$true;gpuTtsHold=(Get-Content -LiteralPath (Join-Path $root 'shared/output/GPU_TTS_HOLD.json') -Raw | ConvertFrom-Json) }
$record | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $target -Encoding utf8
[ordered]@{output=$Output;observedAt=$record.observedAt;cpuLoadPercent=$cpu;ownHeavyJobs=$heavy.Count;gpu=$gpu;foreignProcessCount=$processes.Count} | ConvertTo-Json -Compress
