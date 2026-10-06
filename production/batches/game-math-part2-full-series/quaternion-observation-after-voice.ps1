param([Parameter(Mandatory=$true)][int]$WaitPid,[Parameter(Mandatory=$true)][int]$ReviewPid,[string]$ForceScenes='19,20')
$ErrorActionPreference='Stop'
$mathRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location -LiteralPath $mathRoot
$mathPredecessor=Get-CimInstance Win32_Process -Filter "ProcessId = $WaitPid"
if ($mathPredecessor) {
 if ($mathPredecessor.CommandLine -notlike '*run-owned-job.ps1*game-math-quaternion-operations*voice*') {throw 'Unexpected predecessor; preserve unrelated processes.'}
 Wait-Process -Id $WaitPid
}
$mathResult=Get-Content -LiteralPath 'shared/output/game-math-quaternion-operations/voice-job-result.json' -Raw -Encoding UTF8 | ConvertFrom-Json
if ($mathResult.exitCode -ne 0) {throw 'Baseline quaternion synthesis failed; inspect before continuation.'}
& "$PSScriptRoot/run-owned-job.ps1" -Project 'game-math-quaternion-operations' -Stage voice -Device cpu -ForceScenes $ForceScenes
if ($LASTEXITCODE -ne 0) {throw 'Added observation narration failed; retain checkpoints.'}
$mathOldReview=Get-CimInstance Win32_Process -Filter "ProcessId = $ReviewPid"
if ($mathOldReview) {
 if ($mathOldReview.CommandLine -notlike '*run-owned-job.ps1*game-math-quaternion-operations*review*') {throw 'Unexpected reviewer process; preserve it.'}
 Wait-Process -Id $ReviewPid
}
& "$PSScriptRoot/run-owned-job.ps1" -Project 'game-math-quaternion-operations' -Stage review
exit $LASTEXITCODE
