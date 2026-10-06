$ErrorActionPreference='Stop'
$mathRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location -LiteralPath $mathRoot
& "$PSScriptRoot/run-owned-job.ps1" -Project 'game-math-euler-axis-angle' -Stage voice -Device cpu -ForceScenes '05,20'
if ($LASTEXITCODE -ne 0) {throw 'Added Euler observation narration failed; preserve all checkpoints.'}
$mathReview=Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',"$PSScriptRoot/run-owned-job.ps1",'-Project','game-math-euler-axis-angle','-Stage','review' -WindowStyle Hidden -PassThru
@{retakeVoiceDriverPid=$PID;reviewPid=$mathReview.Id;startedAt=[DateTime]::UtcNow.ToString('o');scenes='05,20';sameApprovedVoice=$true} | ConvertTo-Json | Set-Content -LiteralPath 'shared/output/game-math-euler-axis-angle/observation-owned-jobs.json' -Encoding UTF8
& "$PSScriptRoot/run-owned-job.ps1" -Project 'game-math-rotation-interpolation' -Stage voice -Device cpu
exit $LASTEXITCODE
