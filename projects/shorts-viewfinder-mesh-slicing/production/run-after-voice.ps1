param([string]$RenderName = 'distinctive-ten-v1-full', [switch]$CaptureOnly)
$ErrorActionPreference = 'Stop'
$projectPath = Split-Path $PSScriptRoot -Parent
$workspacePath = Split-Path (Split-Path $projectPath -Parent) -Parent
$slug = Split-Path $projectPath -Leaf
$control = Get-Content -LiteralPath (Join-Path $workspacePath 'shared/publishing/video-production-control.json') -Raw | ConvertFrom-Json
$scope = $control.scopedBatchAuthorizations.'explicit-ten-distinctive-shorts-20261025'
if ($scope.status -ne 'active' -or -not $scope.fullProductionAuthorized -or $slug -notin $scope.slugs) { throw 'Batch inactive for this project' }
$captions = Get-Content -LiteralPath (Join-Path $projectPath 'script/captions.json') -Raw | ConvertFrom-Json
if (-not $captions.timingInputs.voiceSha256) { throw 'Actual voice alignment is required first' }
$localPath = Join-Path $PSScriptRoot 'local'
$capturePath = Join-Path $localPath 'unity-capture'
if (Test-Path -LiteralPath $capturePath) { throw 'Preserve existing native capture; inspect or select a new revision before rerunning' }
python (Join-Path $PSScriptRoot 'prepare-visual.py') --plan-only
if ($LASTEXITCODE -ne 0) { throw 'Phase plan failed' }
$topic = if ($slug -like '*viewfinder*') { 'ViewfinderLesson' } else { 'GravityLesson' }
$unityArgs = @('-batchmode','-projectPath',(Join-Path $localPath 'unity-render'),'-force-d3d11','-force-driver-type-warp','-job-worker-count','2','-shadercompiler-threads','2','-executeMethod',"YamyamCoding.$topic.Editor.Capture.Run",'-lessonOutput',$capturePath,'-lessonFrames',[string]$captions.frames,'-lessonPhaseFile',(Join-Path $localPath 'native-phase-plan.json'),'-logFile',(Join-Path $localPath 'unity-capture.log'))
$unityJob = Start-Process -FilePath 'C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe' -ArgumentList $unityArgs -WindowStyle Hidden -PassThru -Wait
if ($unityJob.ExitCode -ne 0) { throw 'CPU native capture failed; inspect its preserved log' }
python (Join-Path $PSScriptRoot 'prepare-visual.py')
if ($LASTEXITCODE -ne 0) { throw 'Visual preparation failed' }
if ($CaptureOnly) { Write-Output 'Native capture and source frames ready. Parent may use its own Motion Canvas server and output path.'; return }
node (Join-Path $PSScriptRoot 'render-visual.cjs') $RenderName
if ($LASTEXITCODE -ne 0) { throw 'Motion Canvas render failed' }
$visualPath = Join-Path $workspacePath "shared/output/motion-canvas/$slug-$RenderName.mp4"
python (Join-Path $PSScriptRoot 'stabilize-header.py') $visualPath
if ($LASTEXITCODE -ne 0) { throw 'Static heading finalization failed' }
Write-Output 'Visual prepared. Parent continues licensed BGM/voice mix, KO/EN captions, four outputs and final QA.'
