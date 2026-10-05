param([Parameter(Mandatory=$true)][int]$WaitPid)
$ErrorActionPreference='Stop'
$mathRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location -LiteralPath $mathRoot
$mathPredecessor=Get-CimInstance Win32_Process -Filter "ProcessId = $WaitPid"
if ($mathPredecessor) {
 if ($mathPredecessor.CommandLine -notlike '*run-owned-job.ps1*game-math-orientation-matrices*voice*') { throw 'Unexpected predecessor; never wait on an unrelated task.' }
 Wait-Process -Id $WaitPid
}
$mathFirst='game-math-orientation-matrices'
$mathResultPath=Join-Path $mathRoot "shared/output/$mathFirst/voice-job-result.json"
$mathResult=Get-Content -LiteralPath $mathResultPath -Raw | ConvertFrom-Json
if ($mathResult.exitCode -ne 0) { throw 'First voice synthesis failed; retain checkpoint and inspect before continuation.' }
$mathRetakePath=Join-Path $mathRoot "projects/$mathFirst/production/retake-queue.json"
$mathRetakes=Get-Content -LiteralPath $mathRetakePath -Raw | ConvertFrom-Json
$mathRetakes.status='synthesizing-current-script'
[IO.File]::WriteAllText($mathRetakePath,($mathRetakes | ConvertTo-Json -Depth 20),[Text.UTF8Encoding]::new($false))
& "$PSScriptRoot/run-owned-job.ps1" -Project $mathFirst -Stage voice -Device cpu -ForceScenes '04,06,09,10,15'
if ($LASTEXITCODE -ne 0) { throw 'Current-script retakes failed; do not accept incomplete narration.' }
$mathRetakes.status='rendered-awaiting-current-readback-and-meaning-review'
[IO.File]::WriteAllText($mathRetakePath,($mathRetakes | ConvertTo-Json -Depth 20),[Text.UTF8Encoding]::new($false))
& "$PSScriptRoot/run-owned-job.ps1" -Project $mathFirst -Stage review
if ($LASTEXITCODE -ne 0) { throw 'Current first-lecture read-back generation failed.' }
$mathNext='game-math-euler-axis-angle'
$mathReview=Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',"$PSScriptRoot/run-owned-job.ps1",'-Project',$mathNext,'-Stage','review' -WindowStyle Hidden -PassThru
$mathRender=Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',"$PSScriptRoot/run-owned-job.ps1",'-Project',$mathNext,'-Stage','render' -WindowStyle Hidden -PassThru
@{voiceDriverPid=$PID;reviewPid=$mathReview.Id;renderPid=$mathRender.Id;device='cpu';startedAt=[DateTime]::UtcNow.ToString('o');reason='Same approved voice; sequential CPU synthesis while unrelated GPU training remains active'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $mathRoot "shared/output/$mathNext/owned-jobs.json") -Encoding UTF8
& "$PSScriptRoot/run-owned-job.ps1" -Project $mathNext -Stage voice -Device cpu
exit $LASTEXITCODE
