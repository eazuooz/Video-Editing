[CmdletBinding()]
param(
    [string]$Project = 'D:\Github\VideoEditing\unity\VideoEditing',
    [switch]$Apply,
    [string]$ExpectedInventorySha256,
    [string]$ExpectedManifestSha256,
    [switch]$DefinitionsOnly
)
$script:ExpectedMainProject = 'D:\Github\VideoEditing\unity\VideoEditing'

function Get-YamyamSha([string]$Path) {
    $stream = [IO.File]::OpenRead($Path)
    $hash = [Security.Cryptography.SHA256]::Create()
    try { ([BitConverter]::ToString($hash.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $stream.Dispose(); $hash.Dispose() }
}
function Get-YamyamTextSha([string]$Value) {
    $hash = [Security.Cryptography.SHA256]::Create()
    try { ([BitConverter]::ToString($hash.ComputeHash([Text.Encoding]::UTF8.GetBytes($Value)))).Replace('-', '').ToLowerInvariant() }
    finally { $hash.Dispose() }
}
function Assert-YamyamOwned([string]$Path, [string]$Boundary) {
    $full = [IO.Path]::GetFullPath($Path).TrimEnd('\')
    $stop = [IO.Path]::GetFullPath($Boundary).TrimEnd('\')
    if ($full -ine $stop -and -not $full.StartsWith($stop + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Outside ownership boundary: $full" }
    $current = $full
    while ($current) {
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -LiteralPath $current -Force -ErrorAction Stop
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse path refused: $current" }
        }
        $parent = [IO.Path]::GetDirectoryName($current)
        if ($parent -eq $current) { break }
        $current = $parent
    }
}
function Get-YamyamUnityProcesses { @(Get-CimInstance Win32_Process -Filter "Name='Unity.exe'" -ErrorAction Stop) }
function Get-YamyamParentProcess([int]$Identifier) { Get-CimInstance Win32_Process -Filter "ProcessId=$Identifier" -ErrorAction Stop }
function Assert-YamyamNoIsolatedUnity([string]$Headless) {
    $processes = @(Get-YamyamUnityProcesses)
    $byId = @{}
    foreach ($entry in $processes) { $byId[[int]$entry.ProcessId] = $entry }
    foreach ($process in $processes) {
        # Hub has a separate, verified Unity-named helper without -projectPath.
        # Every actual Editor/worker remains subject to exact ownership checks.
        if ($process.ExecutablePath -ieq 'C:\Program Files\Unity Hub\resources\unity.exe') { continue }
        if ($process.ExecutablePath -ine 'C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe') { throw "Unknown Unity executable for PID $($process.ProcessId): $($process.ExecutablePath)" }
        $current = $process
        $visited = [Collections.Generic.HashSet[int]]::new()
        while ($current) {
            if (-not $visited.Add([int]$current.ProcessId) -or $visited.Count -gt 32) { throw 'Unity parent chain is cyclic or exceeds the bounded guard' }
            $match = [regex]::Match([string]$current.CommandLine, '(?i)(?:^|\s)-projectPath\s+(?:"(?<path>[^"]+)"|(?<path>\S+))')
            if ($match.Success) {
                if (-not [IO.Path]::IsPathRooted($match.Groups['path'].Value)) { throw "Unity project path is not absolute for PID $($current.ProcessId)" }
                if ([IO.Path]::GetFullPath($match.Groups['path'].Value).TrimEnd('\/') -ieq [IO.Path]::GetFullPath($Headless).TrimEnd('\/')) { throw "Isolated Unity is still running: PID $($current.ProcessId)" }
            }
            $parent = $null
            if ([int]$current.ParentProcessId -gt 0) {
                if ($byId.ContainsKey([int]$current.ParentProcessId)) { $parent = $byId[[int]$current.ParentProcessId] }
                else { $parent = Get-YamyamParentProcess ([int]$current.ParentProcessId) }
            }
            if ($parent -and $parent.ExecutablePath -ieq 'C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe') { $current = $parent; continue }
            if ($parent -and $parent.Name -ieq 'Unity.exe' -and $parent.ExecutablePath -ine 'C:\Program Files\Unity Hub\resources\unity.exe') { throw "Unknown Unity executable in parent chain for PID $($parent.ProcessId)" }
            if (-not $match.Success) { throw "Cannot establish absolute project ownership for root Editor PID $($current.ProcessId)" }
            break
        }
    }
    $lockPath = Join-Path $Headless 'Temp\UnityLockfile'
    if (Test-Path -LiteralPath $lockPath) {
        Assert-YamyamOwned $lockPath $Headless
        try { $handle = [IO.File]::Open($lockPath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::None); $handle.Dispose() }
        catch { throw "Isolated Unity lock remains held or unreadable: $lockPath" }
    }
}
function Get-YamyamTerrainInventory([string]$Root, [string]$Boundary) {
    Assert-YamyamOwned $Root $Boundary
    Assert-YamyamOwned ($Root + '.meta') $Boundary
    if (-not (Test-Path -LiteralPath $Root -PathType Container) -or -not (Test-Path -LiteralPath ($Root + '.meta') -PathType Leaf)) { throw 'Generated terrain directory and paired folder.meta are required together' }
    $files = [Collections.Generic.List[object]]::new()
    $directories = [Collections.Generic.List[string]]::new()
    $pending = [Collections.Generic.Stack[string]]::new(); $pending.Push($Root)
    while ($pending.Count) {
        $directory = $pending.Pop()
        foreach ($item in @(Get-ChildItem -LiteralPath $directory -Force -ErrorAction Stop)) {
            Assert-YamyamOwned $item.FullName $Boundary
            $relative = $item.FullName.Substring($Root.Length + 1).Replace('\', '/')
            if ($item.PSIsContainer) { $directories.Add($relative); $pending.Push($item.FullName) }
            else { $files.Add([ordered]@{ path = $relative; bytes = $item.Length; sha256 = Get-YamyamSha $item.FullName }) }
        }
    }
    $meta = Get-Item -LiteralPath ($Root + '.meta') -Force
    $guidMatch = [regex]::Match([IO.File]::ReadAllText($meta.FullName), '(?m)^guid:\s*([a-fA-F0-9]{32})\s*$')
    if (-not $guidMatch.Success) { throw 'Generated terrain folder metadata has no valid GUID' }
    $result = [ordered]@{ directories = @($directories | Sort-Object -CaseSensitive); files = @($files | Sort-Object -Property path -CaseSensitive); folderMeta = [ordered]@{ bytes = $meta.Length; sha256 = Get-YamyamSha $meta.FullName; guid = $guidMatch.Groups[1].Value.ToLowerInvariant() } }
    $json = ConvertTo-Json -InputObject $result -Depth 12 -Compress
    $payloadBytes = [long]0
    foreach ($entry in $files) { $payloadBytes += [long]$entry.bytes }
    [ordered]@{ inventorySha256 = Get-YamyamTextSha $json; inventory = $result; files = $files.Count; bytes = $payloadBytes + $meta.Length }
}
function Save-YamyamRetirementReport([string]$Path, [object]$Report, [string]$Boundary) {
    Assert-YamyamOwned $Path $Boundary
    $temporary = $Path + '.' + [guid]::NewGuid().ToString('N') + '.tmp'
    [IO.File]::WriteAllText($temporary, (ConvertTo-Json -InputObject $Report -Depth 25) + "`n", [Text.UTF8Encoding]::new($false))
    for ($attempt = 0; ; $attempt++) {
        try { if ([IO.File]::Exists($Path)) { [IO.File]::Replace($temporary, $Path, [NullString]::Value) } else { [IO.File]::Move($temporary, $Path) }; return }
        catch {
            $errorValue = $_.Exception
            while ($errorValue.InnerException) { $errorValue = $errorValue.InnerException }
            $code = $errorValue.HResult -band 65535
            if ($attempt -ge 4 -or $code -notin @(5, 32, 33, 1175)) { throw "Report write failed; newest evidence retained at ${temporary}: $_" }
            Start-Sleep -Milliseconds (100 * ($attempt + 1))
        }
    }
}
function Move-YamyamOwnedItem([string]$Source, [string]$Destination) { Move-Item -LiteralPath $Source -Destination $Destination -ErrorAction Stop }
function Invoke-YamyamTerrainRetirement([string]$MainProject, [bool]$DoApply, [string]$ExpectedInventory, [string]$ExpectedManifest) {
    $main = [IO.Path]::GetFullPath($MainProject).TrimEnd('\')
    if ($main -ine [IO.Path]::GetFullPath($script:ExpectedMainProject).TrimEnd('\')) { throw 'Only the exact original main project is authorized' }
    $work = Join-Path $main 'Library\YamyamAssetLibrary'
    $headless = Join-Path $work 'headless-project'
    $source = Join-Path $headless 'Assets\_TerrainAutoUpgrade'
    $sourceMeta = $source + '.meta'
    $manifestPath = Join-Path $work 'staging-manifest.json'
    foreach ($path in @($work, $headless, $source, $sourceMeta, $manifestPath)) { Assert-YamyamOwned $path $main }
    Assert-YamyamNoIsolatedUnity $headless
    $latestPath = Join-Path $work 'terrain-generated-retirement-latest.json'
    if (Test-Path -LiteralPath $latestPath) {
        Assert-YamyamOwned $latestPath $main
        $latest = Get-Content -LiteralPath $latestPath -Raw | ConvertFrom-Json
        if ($latest.status -eq 'retired') {
            if ((Test-Path -LiteralPath $source) -or (Test-Path -LiteralPath $sourceMeta)) { throw 'Already retired once; a reappeared generated tree belongs to a later job and must not be retired again' }
            return $latest
        }
    }
    $manifestSha = Get-YamyamSha $manifestPath
    if ($ExpectedManifest -and $ExpectedManifest -cne $manifestSha) { throw 'Canonical manifest differs from the explicitly expected SHA' }
    $before = Get-YamyamTerrainInventory $source $main
    if ($ExpectedInventory -and $ExpectedInventory -cne $before.inventorySha256) { throw 'Generated tree differs from the explicitly expected inventory SHA' }
    $run = Join-Path $work ('terrain-generated-retirement\' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmss') + '-' + [guid]::NewGuid().ToString('N'))
    $destination = Join-Path $run 'Assets\_TerrainAutoUpgrade'
    $destinationMeta = $destination + '.meta'
    foreach ($path in @($run, $destination, $destinationMeta)) { Assert-YamyamOwned $path $work }
    if ((Test-Path -LiteralPath $destination) -or (Test-Path -LiteralPath $destinationMeta)) { throw 'Retirement destination already exists' }
    New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force -ErrorAction Stop | Out-Null
    $reportPath = Join-Path $run 'report.json'
    $report = [ordered]@{ schemaVersion = 1; status = 'ready-dry-run'; apply = $DoApply; startedUtc = [DateTime]::UtcNow.ToString('o'); completedUtc = $null; mainProject = $main; isolatedProject = $headless; source = $source; sourceMeta = $sourceMeta; destination = $destination; destinationMeta = $destinationMeta; reportPath = $reportPath; manifestPath = $manifestPath; manifestSha256 = $manifestSha; inventorySha256 = $before.inventorySha256; inventory = $before.inventory; files = $before.files; bytes = $before.bytes; metaMoved = $false; treeMoved = $false; rollbackAttempted = $false; rollbackErrors = @(); originalArchivesModified = $false; canonicalManifestModified = $false; purpose = 'Preserve pre-repair native Terrain auto-upgrade outputs outside Assets before fresh repaired-source imports. Later generated outputs must not be retired again.' }
    try {
        Save-YamyamRetirementReport $reportPath $report $main
        if ($DoApply) {
            Assert-YamyamNoIsolatedUnity $headless
            if ((Get-YamyamSha $manifestPath) -cne $manifestSha -or (Get-YamyamTerrainInventory $source $main).inventorySha256 -cne $before.inventorySha256) { throw 'Sources changed during retirement preflight' }
            $original = Join-Path $run 'pre-move-backup\_TerrainAutoUpgrade'
            Assert-YamyamOwned $original $work
            New-Item -ItemType Directory -Path $original -Force -ErrorAction Stop | Out-Null
            foreach ($entry in $before.inventory.files) {
                $copyPath = Join-Path $original $entry.path
                Assert-YamyamOwned $copyPath $work
                New-Item -ItemType Directory -Path (Split-Path -Parent $copyPath) -Force -ErrorAction Stop | Out-Null
                [IO.File]::Copy((Join-Path $source $entry.path), $copyPath, $false)
            }
            foreach ($directory in $before.inventory.directories) { New-Item -ItemType Directory -Path (Join-Path $original $directory) -Force -ErrorAction Stop | Out-Null }
            [IO.File]::Copy($sourceMeta, ($original + '.meta'), $false)
            if ((Get-YamyamTerrainInventory $original $main).inventorySha256 -cne $before.inventorySha256) { throw 'Independent pre-move backup failed verification' }
            $report.originalBackup = $original
            $report.status = 'moving'; Save-YamyamRetirementReport $reportPath $report $main
            Move-YamyamOwnedItem $sourceMeta $destinationMeta
            $report.metaMoved = $true; Save-YamyamRetirementReport $reportPath $report $main
            Move-YamyamOwnedItem $source $destination
            $report.treeMoved = $true; Save-YamyamRetirementReport $reportPath $report $main
            $after = Get-YamyamTerrainInventory $destination $main
            if ($after.inventorySha256 -cne $before.inventorySha256) { throw 'Retired inventory/metadata hashes differ from preserved source' }
            $report.status = 'retired'; $report.backupInventorySha256 = $after.inventorySha256
        }
    }
    catch {
        $report.status = 'failed'; $report.error = $_.Exception.ToString(); $report.rollbackAttempted = $report.metaMoved -or $report.treeMoved
        if ($report.metaMoved -and -not (Test-Path -LiteralPath $destinationMeta) -and -not (Test-Path -LiteralPath $sourceMeta) -and $report.originalBackup) {
            try { [IO.File]::Copy(($report.originalBackup + '.meta'), $destinationMeta, $false); $report.folderMetadataRestoredFromBackup = $true }
            catch { $report.rollbackErrors += $_.Exception.Message }
        }
        if ($report.treeMoved) {
            try {
                if (Test-Path -LiteralPath $source) { throw 'A newer source tree exists; preserving both locations' }
                if ((Get-YamyamTerrainInventory $destination $main).inventorySha256 -cne $before.inventorySha256) { throw 'Destination tree changed; preserving newer bytes' }
                Move-YamyamOwnedItem $destination $source; $report.treeMoved = $false
            } catch { $report.rollbackErrors += $_.Exception.Message }
        }
        if ($report.metaMoved -and -not $report.treeMoved) {
            try {
                if (Test-Path -LiteralPath $sourceMeta) { throw 'A newer source folder.meta exists; preserving both locations' }
                if ((Get-YamyamSha $destinationMeta) -cne $before.inventory.folderMeta.sha256) { throw 'Destination folder.meta changed; preserving newer bytes' }
                Move-YamyamOwnedItem $destinationMeta $sourceMeta; $report.metaMoved = $false
            } catch { $report.rollbackErrors += $_.Exception.Message }
        }
        $report.rollbackComplete = -not $report.treeMoved -and -not $report.metaMoved -and $report.rollbackErrors.Count -eq 0
    }
    $report.completedUtc = [DateTime]::UtcNow.ToString('o')
    Save-YamyamRetirementReport $reportPath $report $main
    Save-YamyamRetirementReport $latestPath $report $main
    return $report
}
if (-not $DefinitionsOnly) {
    $result = Invoke-YamyamTerrainRetirement $Project $Apply.IsPresent $ExpectedInventorySha256 $ExpectedManifestSha256
    [pscustomobject]$result | Select-Object status, files, bytes, inventorySha256, reportPath, rollbackComplete, error | ConvertTo-Json -Compress
    if ($result.status -notin @('retired', 'ready-dry-run')) { exit 1 }
}
