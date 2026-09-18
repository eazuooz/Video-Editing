param([switch]$Apply)

# Project-scoped cleanup only. Dry run is the default; no tracked file is deleted.
$ErrorActionPreference = 'Stop'
$cleanupRepo = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot)).TrimEnd('\', '/')
$cleanupBoundary = $cleanupRepo + [IO.Path]::DirectorySeparatorChar
$cleanupTracked = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($file in (& git -C $cleanupRepo -c core.quotepath=false ls-files)) { [void]$cleanupTracked.Add($file) }
if ($LASTEXITCODE -ne 0) { throw 'Cannot verify tracked files.' }

function Assert-SafeCleanupPath([string]$Path) {
    $resolved = (Resolve-Path -LiteralPath $Path).ProviderPath
    if (-not $resolved.StartsWith($cleanupBoundary, [StringComparison]::OrdinalIgnoreCase)) { throw "Outside workspace: $resolved" }
    $cursor = Get-Item -LiteralPath $resolved -Force
    while ($cursor.FullName -ne $cleanupRepo) {
        if (($cursor.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Refusing linked path: $($cursor.FullName)" }
        $cursor = Get-Item -LiteralPath (Split-Path -Parent $cursor.FullName) -Force
    }
    return $resolved
}

$cleanupItems = [Collections.Generic.List[object]]::new()
function Add-CleanupFile($File, [string]$Reason) {
    $resolved = Assert-SafeCleanupPath $File.FullName
    $relative = $resolved.Substring($cleanupBoundary.Length).Replace('\', '/')
    if ($cleanupTracked.Contains($relative)) { throw "Refusing tracked file: $relative" }
    & git -C $cleanupRepo check-ignore -q -- $relative
    if ($LASTEXITCODE -ne 0) { throw "Refusing non-ignored file: $relative" }
    $cleanupItems.Add([pscustomobject]@{Path=$relative;Bytes=[long]$File.Length;Reason=$Reason})
}

$cacheRules = @(
    @{Path='shared/output/visible-rewards/media-cache';Reason='download-and-cut-cache';Extensions=@('.mp4','.webm','.mkv','.m4a','.wav','.mp3','.part','.jpg','.jpeg','.png','.ffconcat')},
    @{Path='shared/output/visible-rewards/media-cache-v2';Reason='download-and-cut-cache';Extensions=@('.mp4','.webm','.mkv','.m4a','.wav','.mp3','.part','.jpg','.jpeg','.png','.ffconcat')},
    @{Path='shared/output/visible-rewards/audio-final-v1';Reason='duplicate-mix-and-stems';Extensions=@('.wav','.m4a')},
    @{Path='shared/output/visible-rewards/audio-final-v2';Reason='duplicate-mix-and-stems';Extensions=@('.wav','.m4a')},
    @{Path='shared/output/visible-rewards/visual-qa-v1';Reason='generated-visual-checks';Extensions=@('.png','.jpg','.mp4','.ffconcat')},
    @{Path='shared/output/visible-rewards/visual-qa-v2';Reason='generated-visual-checks';Extensions=@('.png','.jpg','.mp4','.ffconcat')},
    @{Path='shared/output/visible-rewards/visual-qa-v3';Reason='generated-visual-checks';Extensions=@('.png','.jpg','.mp4','.ffconcat')},
    @{Path='shared/output/narration/visible-rewards/qwen3-1.7b-balanced-v1/chunks';Reason='intermediate-tts-chunks';Extensions=@('.wav')}
)
foreach ($rule in $cacheRules) {
    $folder = Join-Path $cleanupRepo $rule.Path
    if (-not (Test-Path -LiteralPath $folder)) { continue }
    [void](Assert-SafeCleanupPath $folder)
    $entries = @(Get-ChildItem -LiteralPath $folder -Recurse -Force)
    if (@($entries | Where-Object { ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 }).Count) { throw "Linked cache entry: $folder" }
    foreach ($entry in $entries) {
        if (-not $entry.PSIsContainer -and $rule.Extensions -contains $entry.Extension.ToLowerInvariant()) { Add-CleanupFile $entry $rule.Reason }
    }
}
$renderFolder = Join-Path $cleanupRepo 'shared/output/motion-canvas'
foreach ($file in Get-ChildItem -LiteralPath $renderFolder -File) {
    if ($file.Name -match '^visible-rewards-(GAME|GRAPHICS)-v[123]-0[1-8]\.mp4$') { Add-CleanupFile $file 'assembly-fragments' }
    elseif ($file.Name -in @('visible-rewards.mp4','visible-rewards-v2.mp4')) { Add-CleanupFile $file 'superseded-video' }
}

# Check final delivery + current editing inputs before and after cleanup.
& node (Join-Path $cleanupRepo 'scripts/verify-visible-rewards-delivery.cjs')
if ($LASTEXITCODE -ne 0) { throw 'Final delivery verification failed.' }
$keptFiles = @(
    'shared/output/motion-canvas/visible-rewards-final.mp4',
    'shared/output/motion-canvas/visible-rewards-final.ko.srt',
    'shared/output/motion-canvas/visible-rewards-final.en.srt',
    'motion-canvas/src/projects/visible-rewards/assets/final-mix-v2.wav',
    'projects/visible-rewards/publishing/thumbnails/visible-rewards-ko-v1.png',
    'projects/visible-rewards/publishing/title.ko.txt',
    'projects/visible-rewards/publishing/title.en.txt',
    'projects/visible-rewards/publishing/description.ko.txt',
    'projects/visible-rewards/publishing/description.en.txt'
)
$keptHashes = @{}
foreach ($file in $keptFiles) { $keptHashes[$file] = (Get-FileHash -LiteralPath (Join-Path $cleanupRepo $file) -Algorithm SHA256).Hash }
$totalBytes = [long](($cleanupItems | Measure-Object Bytes -Sum).Sum)
$summary = @($cleanupItems | Group-Object Reason | ForEach-Object { [pscustomobject]@{Reason=$_.Name;Files=$_.Count;Bytes=[long](($_.Group | Measure-Object Bytes -Sum).Sum)} })
$summary | ConvertTo-Json -Compress
Write-Output "Candidates: $($cleanupItems.Count) files / $totalBytes bytes / $([math]::Round($totalBytes/1GB,3)) GiB. Apply=$Apply"
if (-not $Apply) { return }

$reportFolder = Join-Path $cleanupRepo 'projects/visible-rewards/maintenance'
[void](New-Item -ItemType Directory -Force -Path $reportFolder)
$reportFile = Join-Path $reportFolder ('cleanup-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json')
$report = [ordered]@{StartedAt=(Get-Date).ToString('o');Scope='visible-rewards-ignored-cache-only';Status='planned';PlannedBytes=$totalBytes;RemovedBytes=0;RemovedFiles=0;PreservedSha256=$keptHashes;Groups=$summary;Files=@($cleanupItems.ToArray());Recovery='Permanent removal. Download/render caches must be regenerated; v1 video also has a retained Git media archive. Local v2 MP4 has no archived exact copy.'}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportFile -Encoding UTF8
try {
    foreach ($item in $cleanupItems) {
        $path = Assert-SafeCleanupPath (Join-Path $cleanupRepo $item.Path)
        if ((Get-Item -LiteralPath $path).Length -ne $item.Bytes) { throw "File changed since inspection: $path" }
        # File-only native deletion; never recursive removal of a computed directory.
        Remove-Item -LiteralPath $path -Force -ErrorAction Stop
        $report.RemovedBytes += $item.Bytes
        $report.RemovedFiles++
    }
    foreach ($file in $keptFiles) {
        if ((Get-FileHash -LiteralPath (Join-Path $cleanupRepo $file) -Algorithm SHA256).Hash -ne $keptHashes[$file]) { throw "Protected file changed: $file" }
    }
    & node (Join-Path $cleanupRepo 'scripts/verify-visible-rewards-delivery.cjs')
    if ($LASTEXITCODE -ne 0) { throw 'Post-cleanup verification failed.' }
    $report.Status = 'completed-protected-files-verified'
} catch {
    $report.Status = 'stopped-review-required'
    throw
} finally {
    $report['FinishedAt'] = (Get-Date).ToString('o')
    $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportFile -Encoding UTF8
}
Write-Output "Removed $($report.RemovedFiles) files / $($report.RemovedBytes) bytes. Report: $reportFile"
