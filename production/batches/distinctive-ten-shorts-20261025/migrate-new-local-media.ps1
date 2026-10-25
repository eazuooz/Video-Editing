param([string[]]$Slugs = @(), [switch]$IncludeBatch)
$ErrorActionPreference = 'Stop'
$taskRepository = 'D:\Github\VideoEditing'
$taskDestinationRoot = 'C:\Users\1\Videos\YamyamProduction\distinctive-ten-shorts-20261025'
$taskBatchRoot = Join-Path $taskRepository 'production\batches\distinctive-ten-shorts-20261025'
$taskBatch = Get-Content -LiteralPath (Join-Path $taskBatchRoot 'batch.json') -Raw | ConvertFrom-Json
$taskTransfers = @()
if ($IncludeBatch) { $taskTransfers += @{ Source = (Join-Path $taskBatchRoot 'local'); Destination = (Join-Path $taskDestinationRoot 'batch-local') } }
foreach ($taskSlug in $Slugs) {
    if ($taskSlug -notin $taskBatch.projects.slug) { throw "Not in this explicitly selected batch: $taskSlug" }
    $taskTransfers += @{ Source = (Join-Path $taskRepository "projects\$taskSlug\production\local"); Destination = (Join-Path $taskDestinationRoot "$taskSlug\local") }
}
New-Item -ItemType Directory -Path $taskDestinationRoot -Force | Out-Null
$taskResults = @()
foreach ($taskTransfer in $taskTransfers) {
    $taskSource = [IO.Path]::GetFullPath($taskTransfer.Source)
    $taskDestination = [IO.Path]::GetFullPath($taskTransfer.Destination)
    if (-not $taskSource.StartsWith($taskRepository + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Source outside intended repository' }
    if (-not $taskDestination.StartsWith($taskDestinationRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Destination outside explicit new-media directory' }
    if (-not (Test-Path -LiteralPath $taskSource)) { New-Item -ItemType Directory -Path $taskSource | Out-Null }
    $taskItem = Get-Item -LiteralPath $taskSource
    if ($taskItem.LinkType -eq 'Junction') {
        if ([IO.Path]::GetFullPath($taskItem.Target) -ne $taskDestination) { throw 'Unexpected existing junction' }
        continue
    }
    $taskResolved = (Resolve-Path -LiteralPath $taskSource).Path
    if ($taskResolved -ne $taskSource -or $taskItem.LinkType) { throw 'Unexpected source resolution or link' }
    if (Test-Path -LiteralPath $taskDestination) { throw "Destination already exists; preserve it: $taskDestination" }
    $taskBefore = @{}
    Get-ChildItem -LiteralPath $taskSource -Recurse -File | ForEach-Object {
        $taskRelative = [IO.Path]::GetRelativePath($taskSource, $_.FullName)
        $taskBefore[$taskRelative] = @{ Length = $_.Length; Sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash }
    }
    New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($taskDestination)) -Force | Out-Null
    Move-Item -LiteralPath $taskSource -Destination $taskDestination
    foreach ($taskRelative in $taskBefore.Keys) {
        $taskFile = Join-Path $taskDestination $taskRelative
        if ((Get-Item -LiteralPath $taskFile).Length -ne $taskBefore[$taskRelative].Length -or (Get-FileHash -LiteralPath $taskFile -Algorithm SHA256).Hash -ne $taskBefore[$taskRelative].Sha256) { throw "Moved file differs: $taskRelative" }
    }
    New-Item -ItemType Junction -Path $taskSource -Target $taskDestination | Out-Null
    $taskResults += @{ Source = $taskSource; Destination = $taskDestination; VerifiedFiles = $taskBefore.Count; SourcePathPreservedByJunction = $true }
}
$taskReceipt = Join-Path $taskBatchRoot ('media-migration-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json')
$taskResults | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $taskReceipt -Encoding utf8
$taskResults | ConvertTo-Json -Depth 5
