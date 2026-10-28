$ErrorActionPreference = 'Stop'
$taskRoot = 'D:\Github\VideoEditing'
$taskBatch = Join-Path $taskRoot 'production\maintenance\published-media-cleanup-20261028'
$planPath = Join-Path $taskBatch 'plan.json'
$plan = Get-Content -Raw -LiteralPath $planPath -Encoding UTF8 | ConvertFrom-Json
$verified = Get-Content -Raw -LiteralPath (Join-Path $taskBatch 'hash-verification.json') -Encoding UTF8 | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $planPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $verified.planSha256) { throw 'Plan changed since verification' }
$hashes = @{}
Get-Content -LiteralPath (Join-Path $taskBatch 'hashes.jsonl') -Encoding UTF8 | ForEach-Object { $row = $_ | ConvertFrom-Json; $hashes[$row.path] = $row.sha256 }
if ($hashes.Count -ne $plan.files.Count) { throw 'Incomplete verification' }
if (Test-Path -LiteralPath (Join-Path $taskBatch 'deletions.jsonl')) { throw 'Deletion log already exists; review outcome before any retry' }
function Assert-SafeFile($entry) {
    $target = [IO.Path]::GetFullPath($entry.absolute)
    if (-not $target.StartsWith($taskRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Outside workspace' }
    if ([IO.Path]::GetPathRoot($target) -ne 'D:\') { throw 'Not on D drive' }
    if ([IO.Path]::GetExtension($target).ToLowerInvariant() -notin @('.mp4','.mov','.mkv','.webm','.m4v','.avi','.wav')) { throw 'Unexpected file type' }
    $item = Get-Item -LiteralPath $target -Force
    if ($item.PSIsContainer) { throw 'Directory deletion prohibited' }
    $node = $item
    while ($null -ne $node -and $node.FullName.Length -ge $taskRoot.Length) {
        if (($node.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Junction/symlink prohibited' }
        if ($node -is [IO.FileInfo]) { $node = $node.Directory } else { $node = $node.Parent }
    }
    $expectedTicks = [long]([decimal]$entry.mtimeNs / 100) + 621355968000000000L
    if ($item.Length -ne $entry.bytes -or [Math]::Abs($item.LastWriteTimeUtc.Ticks - $expectedTicks) -gt 2) { throw 'File changed since inventory' }
    return $target
}
# Validate all concrete absolute targets before deleting the first file.
foreach ($entry in $plan.files) { $null = Assert-SafeFile $entry }
$before = (Get-PSDrive -Name D).Free
$logPath = Join-Path $taskBatch 'deletions.jsonl'
$writer = [IO.StreamWriter]::new($logPath,$false,[Text.UTF8Encoding]::new($false)); $writer.AutoFlush=$true
$deleted = 0; [long]$deletedBytes=0; $failed=0
try {
    foreach ($entry in $plan.files) {
        $record = [ordered]@{path=$entry.path; absolute=$entry.absolute; owner=$entry.owner; videoId=$entry.videoId; bytes=$entry.bytes; sha256=$hashes[$entry.path]; attemptedAt=[DateTime]::UtcNow.ToString('o')}
        try {
            $target = Assert-SafeFile $entry
            # A file actively held for writing is retained.
            $handle=[IO.File]::Open($target,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::None);$handle.Dispose()
            Remove-Item -LiteralPath $target -ErrorAction Stop
            if (Test-Path -LiteralPath $target) { throw 'File still exists' }
            $record.status='deleted';$deleted++;$deletedBytes+=$entry.bytes
        } catch { $record.status='preserved-error';$record.error=$_.Exception.Message;$failed++ }
        $writer.WriteLine(($record | ConvertTo-Json -Compress))
        if (($deleted+$failed)%2000 -eq 0) { Write-Output "Processed $($deleted+$failed); deleted $deleted; preserved errors $failed" }
    }
} finally { $writer.Dispose() }
$result=[ordered]@{completedAt=[DateTime]::UtcNow.ToString('o');deletedFiles=$deleted;deletedBytes=$deletedBytes;preservedErrors=$failed;driveFreeBefore=$before;driveFreeAfter=(Get-PSDrive -Name D).Free;platformMutations=0;recursiveDeletes=0}
$result | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskBatch 'result.json') -Encoding UTF8
$result | ConvertTo-Json -Compress
