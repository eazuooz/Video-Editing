param(
    [Parameter(Mandatory=$true)][string]$Project,
    [Parameter(Mandatory=$true)][ValidateSet('voice','review','render')][string]$Stage,
    [ValidateSet('cpu','cuda:0')][string]$Device = 'cuda:0',
    [string]$ForceScenes = '',
    [string]$Scenes = '',
    [string]$ReplacementBaseline = '',
    [ValidateSet('','projection-episode-split-v1','projection-viewport-pair-v1','projection-depth-v1','mesh-uv-precision-v1')][string]$VoiceWorkflow = ''
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
    if ($Scenes) { $mathArgs += @('--scenes',$Scenes) }
    if ($VoiceWorkflow -eq 'projection-episode-split-v1') {
        if ($Project -ne 'game-math-camera-projection') { throw 'Projection episode workflow is scoped to its current project.' }
        $mathArgs = @('-X','utf8',"$PSScriptRoot\render-projection-episode-voice.py",'--project',$Project,'--device',$Device)
    }
    if ($VoiceWorkflow -eq 'projection-viewport-pair-v1') {
        if ($Project -ne 'game-math-camera-projection') { throw 'Viewport pair repair is scoped to its current project.' }
        $mathArgs = @('-X','utf8',"$PSScriptRoot\repair-scene-by-lines.py",$Project,'15','--device',$Device,'--defer-assembly')
    }
    if ($VoiceWorkflow -eq 'projection-depth-v1') {
        if ($Project -ne 'game-math-projection-depth') { throw 'Depth narration workflow is scoped to its current project.' }
        $mathArgs = @('-X','utf8',"$PSScriptRoot\render-projection-depth-voice.py",'--project',$Project,'--device',$Device)
    }
    if ($VoiceWorkflow -eq 'mesh-uv-precision-v1') {
        if ($Project -ne 'game-math-mesh-uv') { throw 'Mesh precision repair is scoped to its current project.' }
        $mathArgs = @('-X','utf8',"$PSScriptRoot\render-mesh-uv-precision-retakes.py",'--device',$Device)
        if ($Scenes) { $mathArgs += @('--scenes',$Scenes) }
    }
    if ($Device -eq 'cuda:0') {
        # Another authorized video may already own the same GPU handoff.
        # Finish that batch and its research resume before requesting ours.
        # Preserve foreign leases/STOP files, including an abandoned lease.
        $mathLease = Join-Path $mathRoot 'shared/output/GPU_HANDOFF.json'
        $mathWaitToken = ''
        while (Test-Path -LiteralPath $mathLease) {
            try { $mathActiveLease = Get-Content -LiteralPath $mathLease -Raw | ConvertFrom-Json }
            catch { Start-Sleep -Seconds 2; continue }
            $mathActiveCoordinator = $null
            if ($mathActiveLease.coordinator.pid) {
                $mathActiveCoordinator = Get-Process -Id $mathActiveLease.coordinator.pid -ErrorAction SilentlyContinue
            }
            if (-not $mathActiveCoordinator) {
                if ([DateTimeOffset]::UtcNow.ToUnixTimeSeconds() - $mathActiveLease.requestedAt -lt 20) {
                    Start-Sleep -Seconds 2; continue
                }
                throw 'A preserved GPU handoff has no live coordinator. Inspect its actual owner; never remove or bypass the lease.'
            }
            $mathCoordinatorCreated = ($mathActiveCoordinator.StartTime.ToUniversalTime() - [DateTime]::new(1970,1,1,0,0,0,[DateTimeKind]::Utc)).TotalSeconds
            if ([Math]::Abs($mathCoordinatorCreated - $mathActiveLease.coordinator.createTime) -gt 0.01) {
                throw 'GPU handoff PID belongs to a different process identity. Preserve the lease and inspect ownership.'
            }
            if ($mathWaitToken -ne $mathActiveLease.token) {
                $mathWaitToken = $mathActiveLease.token
                @{project=$Project;status='waiting-for-existing-video-tts-and-research-resume';existingProject=$mathActiveLease.project;existingToken=$mathActiveLease.token;requestedAt=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $mathWork 'gpu-wait.json') -Encoding UTF8
                Write-Output "Waiting for existing GPU TTS batch: $($mathActiveLease.project)"
            }
            Start-Sleep -Seconds 10
        }
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
    $Device = $mathReviewDevice
    $mathArgs = @('-X','utf8',"$PSScriptRoot\review-voice.py",'--project',$Project,'--watch','--device',$mathReviewDevice)
    if ($Scenes) { $mathArgs += @('--scenes',$Scenes) }
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
