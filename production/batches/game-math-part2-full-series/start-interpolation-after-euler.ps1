param([Parameter(Mandatory=$true)][int]$WaitPid)
$ErrorActionPreference='Stop'
$mathRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location -LiteralPath $mathRoot
$mathPredecessor=Get-CimInstance Win32_Process -Filter "ProcessId = $WaitPid"
if ($mathPredecessor) {
 if ($mathPredecessor.CommandLine -notlike '*finish-voice-and-next.ps1*') {throw 'Unexpected predecessor; preserve unrelated processes.'}
 Wait-Process -Id $WaitPid
}
$mathResult=Get-Content -LiteralPath 'shared/output/game-math-euler-axis-angle/voice-job-result.json' -Raw -Encoding UTF8 | ConvertFrom-Json
if ($mathResult.exitCode -ne 0) {throw 'Euler synthesis did not finish successfully.'}
$mathSlug='game-math-rotation-interpolation'
$mathReviewRecord=Get-Content -LiteralPath "projects/$mathSlug/production/lookdev-review.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$mathManifest=Get-Content -LiteralPath "projects/$mathSlug/project.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$mathModuleHash=(Get-FileHash -LiteralPath $mathManifest.paths.sharedManimLesson -Algorithm SHA256).Hash.ToLower()
$mathDataHash=(Get-FileHash -LiteralPath "$PSScriptRoot/lessons/$mathSlug.json" -Algorithm SHA256).Hash.ToLower()
if ($mathReviewRecord.images.Count -ne 18 -or $mathReviewRecord.renderModuleSha256 -ne $mathModuleHash -or $mathReviewRecord.lessonDataSha256 -ne $mathDataHash) {throw 'Current direct lookdev review is required before synthesis.'}
$mathReview=Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',"$PSScriptRoot/run-owned-job.ps1",'-Project',$mathSlug,'-Stage','review' -WindowStyle Hidden -PassThru
$mathRender=Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',"$PSScriptRoot/run-owned-job.ps1",'-Project',$mathSlug,'-Stage','render' -WindowStyle Hidden -PassThru
@{voiceDriverPid=$PID;reviewPid=$mathReview.Id;renderPid=$mathRender.Id;device='cpu';startedAt=[DateTime]::UtcNow.ToString('o');reason='Current full script/18 direct lookdev sheets verified. Same approved personal Qwen CPU voice after Euler, maximum two own TTS models while other training is preserved.'} | ConvertTo-Json | Set-Content -LiteralPath "shared/output/$mathSlug/owned-jobs.json" -Encoding UTF8
& "$PSScriptRoot/run-owned-job.ps1" -Project $mathSlug -Stage voice -Device cpu
exit $LASTEXITCODE
