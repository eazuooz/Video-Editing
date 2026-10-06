param(
    [Parameter(Mandatory=$true)][string]$Project,
    [Parameter(Mandatory=$true)][ValidateSet('voice','review','render')][string]$Stage,
    [ValidateSet('cpu','cuda:0')][string]$Device = 'cpu',
    [string]$ForceScenes = ''
)
$ErrorActionPreference = 'Stop'
$mathRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
$mathPython = Join-Path $mathRoot 'qwen3-tts\.venv\Scripts\python.exe'
$mathWork = Join-Path $mathRoot "shared\output\$Project"
New-Item -ItemType Directory -Path $mathWork -Force | Out-Null
$mathLog = Join-Path $mathWork "$Stage-job.log"
Set-Location -LiteralPath $mathRoot
if ($Stage -eq 'voice') {
    $mathArgs = @('-X','utf8',"$PSScriptRoot\render-voice.py",'--project',$Project,'--batch-size','1','--device',$Device)
    if ($ForceScenes) { $mathArgs += @('--force-scenes',$ForceScenes) }
} elseif ($Stage -eq 'review') {
    $mathReviewDevice = if ($Device -eq 'cuda:0') { 'cuda' } else { 'cpu' }
    $mathArgs = @('-X','utf8',"$PSScriptRoot\review-voice.py",'--project',$Project,'--watch','--device',$mathReviewDevice)
} else {
    $mathArgs = @('-X','utf8',"$PSScriptRoot\incremental-render.py",$Project)
}
# Windows PowerShell treats harmless native stderr warnings as ErrorRecords.
# Let Python's actual exit code decide success; retain all warnings in the log.
$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
& $mathPython @mathArgs *> $mathLog
$mathExit = $LASTEXITCODE
@{project=$Project;stage=$Stage;device=$Device;exitCode=$mathExit;finishedAt=[DateTime]::UtcNow.ToString('o');log=$mathLog} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $mathWork "$Stage-job-result.json") -Encoding UTF8
exit $mathExit
