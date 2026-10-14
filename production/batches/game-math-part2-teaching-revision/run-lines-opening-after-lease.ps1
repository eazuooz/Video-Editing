$ErrorActionPreference = 'Stop'
$taskRoot = 'D:\Github\Video-Editing'
$leasePath = Join-Path $taskRoot 'shared\output\GPU_HANDOFF.json'
$deadline = (Get-Date).AddHours(3)
$lastState = ''
while ($true) {
 while (Test-Path -LiteralPath $leasePath) {
  $currentLease = Get-Content -LiteralPath $leasePath -Raw -Encoding UTF8 | ConvertFrom-Json
  $newState = "$($currentLease.project):$($currentLease.state)"
  if ($newState -ne $lastState) { Write-Output "Preserving current GPU lease: $newState"; $lastState = $newState }
  if ((Get-Date) -gt $deadline) { throw 'Foreign GPU lease still active; no controls changed.' }
  Start-Sleep -Seconds 15
 }
# Let the returned research queue actually start before requesting its next boundary.
# A PowerShell waiter avoids being mistaken for a GPU Python worker by that queue.
Start-Sleep -Seconds 45
 if (Test-Path -LiteralPath $leasePath) { Write-Output 'Another owner acquired the lease during the research return interval; keep waiting without changing controls.'; continue }
 break
}
Write-Output 'Requesting a normal research job boundary for one clarified new narration opening.'
Set-Location -LiteralPath $taskRoot
& 'C:\Users\eazuo\anaconda3\envs\renderformer\python.exe' -u -X utf8 'production/batches/game-math-part2-full-series/gpu-handoff.py' --project game-math-lines-opening-retake-v4 --queue-dir 'C:/Users/eazuo/renderformer/tmp/placement_focus_20261008' --gpu-idle-timeout 600 -- 'D:/Github/Video-Editing/qwen3-tts/.venv/Scripts/python.exe' -X utf8 'production/batches/game-math-part2-teaching-revision/render-lines-opening-v4.py' --project game-math-lines-opening-retake-v4 --device cuda:0 --batch-size 1
exit $LASTEXITCODE
