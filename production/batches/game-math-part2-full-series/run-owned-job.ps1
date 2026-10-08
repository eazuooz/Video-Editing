param(
    [Parameter(Mandatory=$true)][string]$Project,
    [Parameter(Mandatory=$true)][ValidateSet('voice','review','render')][string]$Stage,
    [ValidateSet('cpu','cuda:0')][string]$Device = 'cuda:0',
    [string]$ForceScenes = '',
    [string]$ReplacementBaseline = ''
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
    if ($Device -eq 'cuda:0') {
        # Finish the active research run before taking GPU ownership, then
        # restore its original queue even when narration fails.
        $mathQueueDir = 'C:/Users/eazuo/renderformer/tmp/placement_focus_20261008'
        $mathQueueOwner = $null
        if (Test-Path -LiteralPath "$mathQueueDir/status.json") {
            $mathQueueStatus = Get-Content -LiteralPath "$mathQueueDir/status.json" -Raw | ConvertFrom-Json
            if ($mathQueueStatus.owner_pid) { $mathQueueOwner = Get-Process -Id $mathQueueStatus.owner_pid -ErrorAction SilentlyContinue }
        }
        if ($mathQueueOwner) {
            $mathArgs = @('-X','utf8',"$PSScriptRoot/gpu-handoff.py",'--project',$Project,'--queue-dir',$mathQueueDir,'--',$mathPython) + $mathArgs
        }
    }
} elseif ($Stage -eq 'review') {
    # Keep read-back on CPU so research regains the GPU immediately after TTS.
    $mathReviewDevice = 'cpu'
    $mathArgs = @('-X','utf8',"$PSScriptRoot\review-voice.py",'--project',$Project,'--watch','--device',$mathReviewDevice)
    if ($ReplacementBaseline) {
        if (-not $ForceScenes) { throw 'Replacement read-back requires the explicit selected scene list.' }
        $mathArgs = @('-X','utf8',"$PSScriptRoot\review-replacements.py",'--project',$Project,'--baseline',$ReplacementBaseline,'--scenes',$ForceScenes)
    }
} else {
    $mathArgs = @('-X','utf8',"$PSScriptRoot\incremental-render.py",$Project)
    if ($ReplacementBaseline) { $mathArgs += @('--await-replacements',$ReplacementBaseline) }
}
# Windows PowerShell treats harmless native stderr warnings as ErrorRecords.
# Let Python's actual exit code decide success; retain all warnings in the log.
$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
& $mathPython @mathArgs *> $mathLog
$mathExit = $LASTEXITCODE
@{project=$Project;stage=$Stage;device=$Device;exitCode=$mathExit;finishedAt=[DateTime]::UtcNow.ToString('o');log=$mathLog} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $mathWork "$Stage-job-result.json") -Encoding UTF8
exit $mathExit
