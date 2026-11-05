@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -Command "$ErrorActionPreference='Stop'; $uri='http://127.0.0.1:9347/output/game-math-remaining-20261104/index.html'; function Ready { try { return (Invoke-WebRequest -UseBasicParsing -Uri $uri -Method Head -TimeoutSec 1).StatusCode -eq 200 } catch { return $false } }; if (-not (Ready)) { $job=Start-Process -FilePath (Get-Command node.exe).Source -ArgumentList 'serve-review.cjs' -WorkingDirectory (Get-Location).Path -WindowStyle Hidden -PassThru; for ($i=0;$i -lt 30 -and -not (Ready);$i++) { if ($job.HasExited) { break }; Start-Sleep -Milliseconds 200 } }; if (-not (Ready)) { throw 'Could not open the local review server on port 9347.' }; Start-Process $uri"
