# Launch the unmodified owned executable with a separate Godot user:// directory.
# Godot 4.1.1 OS_Windows::get_config_path() honors process APPDATA.
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$isolatedRoot = Join-Path $projectRoot 'production/local/original-user-data'
New-Item -ItemType Directory -Force -Path (Join-Path $isolatedRoot 'Roaming'), (Join-Path $isolatedRoot 'Local') | Out-Null
$startInfo = New-Object System.Diagnostics.ProcessStartInfo
$startInfo.FileName = 'D:/SteamLibrary/steamapps/common/Buckshot Roulette/Buckshot Roulette_windows/Buckshot Roulette.exe'
$startInfo.WorkingDirectory = Split-Path $startInfo.FileName
$startInfo.UseShellExecute = $false
$startInfo.EnvironmentVariables['APPDATA'] = Join-Path $isolatedRoot 'Roaming'
$startInfo.EnvironmentVariables['LOCALAPPDATA'] = Join-Path $isolatedRoot 'Local'
$startInfo.Arguments = '--windowed --resolution 1920x1080'
$process = [System.Diagnostics.Process]::Start($startInfo)
@{ pid=$process.Id; startedAt=(Get-Date).ToUniversalTime().ToString('o'); isolatedAppData=$startInfo.EnvironmentVariables['APPDATA']; source=$startInfo.FileName; sourceModified=$false } | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $isolatedRoot 'launch.json')
Write-Output "Launched original game PID $($process.Id) with isolated APPDATA"
