param([Parameter(Mandatory=$true)][string]$Project)
$ErrorActionPreference='Stop'
$mathRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location -LiteralPath $mathRoot
$mathPython=Join-Path $mathRoot 'qwen3-tts\.venv\Scripts\python.exe'
$mathWork=Join-Path $mathRoot "shared/output/$Project"
New-Item -ItemType Directory -Path $mathWork -Force | Out-Null
foreach ($mathStage in @('render','assemble','burn','qa')) {
 $mathLog=Join-Path $mathWork "final-$mathStage.log"
 $ErrorActionPreference='Continue'
 & $mathPython -X utf8 "$PSScriptRoot/build.py" $Project $mathStage *> $mathLog
 $mathExit=$LASTEXITCODE
 $ErrorActionPreference='Stop'
 [IO.File]::WriteAllText((Join-Path $mathWork 'final-stage-result.json'),(@{project=$Project;stage=$mathStage;exitCode=$mathExit;finishedAt=[DateTime]::UtcNow.ToString('o');log=$mathLog;directVisualReview='pending'} | ConvertTo-Json),[Text.UTF8Encoding]::new($false))
 if ($mathExit -ne 0) { exit $mathExit }
}
