param(
    [Parameter(Mandatory = $true)][string]$Project,
    [ValidateSet('Build', 'Inventory', 'Audit', 'Plan', 'Candidates', 'VerifyGzip')][string]$Mode = 'Audit',
    [string]$UnityData
)
$ErrorActionPreference = 'Stop'
$projectPath = [IO.Path]::GetFullPath($Project)
$codeRoot = $PSScriptRoot
$work = Join-Path $projectPath 'Library\YamyamAssetLibrary'
$build = Join-Path $work 'code-inventory-tool'
New-Item -ItemType Directory -Force -Path $build | Out-Null
if (-not $UnityData) {
    $versionText = [IO.File]::ReadAllText((Join-Path $projectPath 'ProjectSettings\ProjectVersion.txt'))
    $version = [regex]::Match($versionText, '(?m)^m_EditorVersion:\s*(\S+)').Groups[1].Value
    $UnityData = Join-Path $env:ProgramFiles ('Unity\Hub\Editor\' + $version + '\Editor\Data')
}
$sdkRoot = Join-Path $UnityData 'DotNetSdk'
$dotnet = Join-Path $sdkRoot 'dotnet.exe'
$sdkVersion = Get-ChildItem -LiteralPath (Join-Path $sdkRoot 'sdk') -Directory | Sort-Object { [version]$_.Name } -Descending | Select-Object -First 1
$referenceVersion = Get-ChildItem -LiteralPath (Join-Path $sdkRoot 'packs\Microsoft.NETCore.App.Ref') -Directory | Sort-Object { [version]$_.Name } -Descending | Select-Object -First 1
$roslyn = Join-Path $sdkVersion.FullName 'Roslyn\bincore'
$refRoot = Get-ChildItem -LiteralPath (Join-Path $referenceVersion.FullName 'ref') -Directory | Sort-Object Name -Descending | Select-Object -First 1
foreach ($dependency in @('Microsoft.CodeAnalysis.dll', 'Microsoft.CodeAnalysis.CSharp.dll')) {
    Copy-Item -LiteralPath (Join-Path $roslyn $dependency) -Destination (Join-Path $build $dependency)
}
$runtime = @{ runtimeOptions = @{ tfm = $refRoot.Name; framework = @{ name = 'Microsoft.NETCore.App'; version = $referenceVersion.Name } } } | ConvertTo-Json -Depth 4
foreach ($tool in @('ExistingCodeInventory', 'VendorCodeAudit', 'VendorSourceRewrite')) {
    $lines = @('/nostdlib+', '/target:exe', '/langversion:latest')
    $lines += ('/out:"' + (Join-Path $build ($tool + '.dll')) + '"')
    $lines += @(Get-ChildItem -LiteralPath $refRoot.FullName -Filter '*.dll' -File | ForEach-Object { '/reference:"' + $_.FullName + '"' })
    foreach ($dependency in @('Microsoft.CodeAnalysis.dll', 'Microsoft.CodeAnalysis.CSharp.dll')) {
        $lines += ('/reference:"' + (Join-Path $roslyn $dependency) + '"')
    }
    $lines += ('"' + (Join-Path $codeRoot ($tool + '.cs')) + '"')
    $response = Join-Path $build ($tool + '.compile.rsp')
    [IO.File]::WriteAllLines($response, $lines, [Text.UTF8Encoding]::new($false))
    [IO.File]::WriteAllText((Join-Path $build ($tool + '.runtimeconfig.json')), $runtime, [Text.UTF8Encoding]::new($false))
    & $dotnet (Join-Path $roslyn 'csc.dll') /noconfig ('@' + $response)
    if ($LASTEXITCODE -ne 0) { throw "$tool compiler exited $LASTEXITCODE" }
}
if ($Mode -eq 'Build') { return }
$inventory = Join-Path $work 'existing-code-inventory.json'
if ($Mode -eq 'Inventory' -or ($Mode -eq 'Audit' -and -not (Test-Path -LiteralPath $inventory))) {
    & $dotnet (Join-Path $build 'ExistingCodeInventory.dll') $projectPath $inventory
    if ($LASTEXITCODE -ne 0) { throw "Inventory exited $LASTEXITCODE" }
    if ($Mode -eq 'Inventory') { return }
}
$audit = Join-Path $work 'vendor-roslyn-preflight.json'
if ($Mode -eq 'Audit') {
    & $dotnet (Join-Path $build 'VendorCodeAudit.dll') (Join-Path $work 'staging-manifest.json') $inventory $audit
    if ($LASTEXITCODE -ne 0) { throw "Audit exited $LASTEXITCODE" }
    return
}
if ($Mode -eq 'Plan') {
    & python (Join-Path $codeRoot 'plan_vendor_adaptations.py') --audit $audit --out (Join-Path $work 'vendor-adaptation-plan.json')
    if ($LASTEXITCODE -ne 0) { throw "Plan exited $LASTEXITCODE" }
    return
}
if ($Mode -eq 'Candidates') {
    & $dotnet (Join-Path $build 'VendorSourceRewrite.dll') (Join-Path $work 'vendor-source-rewrite-operations.json') (Join-Path $work 'vendor-source-rewrite-receipts.json')
    if ($LASTEXITCODE -ne 0) { throw "Candidate rewrite exited $LASTEXITCODE" }
}
if ($Mode -eq 'VerifyGzip') {
    $plan = Get-Content -LiteralPath (Join-Path $work 'vendor-adaptation-plan.json') -Raw | ConvertFrom-Json
    $operation = @($plan.operations | Where-Object { $_.portGzip })
    if ($operation.Count -ne 1) { throw 'Expected exactly one reviewed GZip candidate' }
    $test = Join-Path $build 'GzipPortVerification.dll'
    $lines = @('/nostdlib+', '/target:exe', '/langversion:latest', ('/out:"' + $test + '"'))
    $lines += @(Get-ChildItem -LiteralPath $refRoot.FullName -Filter '*.dll' -File | ForEach-Object { '/reference:"' + $_.FullName + '"' })
    $lines += ('"' + (Join-Path $codeRoot 'GzipPortVerification.cs') + '"')
    $lines += ('"' + $operation[0].outputPath + '"')
    $response = Join-Path $build 'GzipPortVerification.compile.rsp'
    [IO.File]::WriteAllLines($response, $lines, [Text.UTF8Encoding]::new($false))
    [IO.File]::WriteAllText((Join-Path $build 'GzipPortVerification.runtimeconfig.json'), $runtime, [Text.UTF8Encoding]::new($false))
    & $dotnet (Join-Path $roslyn 'csc.dll') /noconfig ('@' + $response)
    if ($LASTEXITCODE -ne 0) { throw "GZip candidate compilation exited $LASTEXITCODE" }
    & $dotnet $test (Join-Path $work 'gzip-port-verification.json')
    if ($LASTEXITCODE -ne 0) { throw "GZip candidate verification exited $LASTEXITCODE" }
}
