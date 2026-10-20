$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'retire-unity-terrain-generated.ps1') -DefinitionsOnly
$script:FixtureProcesses = @()
function Get-YamyamUnityProcesses { @($script:FixtureProcesses) }
function Get-YamyamParentProcess([int]$Identifier) { $null }
$script:MoveFault = ''
function Move-YamyamOwnedItem([string]$Source, [string]$Destination) {
    if ($script:MoveFault -eq 'directory' -and (Test-Path -LiteralPath $Source -PathType Container)) { $script:MoveFault = ''; throw 'fixture directory rename failed' }
    Move-Item -LiteralPath $Source -Destination $Destination -ErrorAction Stop
    if ($script:MoveFault -eq 'foreign' -and (Test-Path -LiteralPath $Destination -PathType Container)) { $script:MoveFault = ''; [IO.File]::WriteAllText((Join-Path $Destination 'one.terrainlayer'), 'newer foreign data') }
}
function Assert-True([bool]$Value, [string]$Message) { if (-not $Value) { throw $Message } }
function Assert-Throws([scriptblock]$Action) { $threw = $false; try { & $Action } catch { $threw = $true }; Assert-True $threw 'Expected safe refusal' }
$temporaryBase = [IO.Path]::GetFullPath((Join-Path ([IO.Path]::GetTempPath()) ('yamyam-terrain-retirement-tests-' + [guid]::NewGuid().ToString('N'))))
New-Item -ItemType Directory -Path $temporaryBase | Out-Null
try {
    $passed = 0
    foreach ($case in @('dry-apply', 'active', 'wrong-input', 'rollback', 'foreign', 'reparse')) {
        $fixture = Join-Path $temporaryBase $case
        $script:ExpectedMainProject = $fixture
        $work = Join-Path $fixture 'Library\YamyamAssetLibrary'
        $headless = Join-Path $work 'headless-project'
        $source = Join-Path $headless 'Assets\_TerrainAutoUpgrade'
        New-Item -ItemType Directory -Path $source -Force | Out-Null
        [IO.File]::WriteAllText((Join-Path $work 'staging-manifest.json'), '{"fixture":true}')
        [IO.File]::WriteAllText((Join-Path $source 'one.terrainlayer'), 'original layer')
        [IO.File]::WriteAllText((Join-Path $source 'one.terrainlayer.meta'), "fileFormatVersion: 2`nguid: 11111111111111111111111111111111`n")
        [IO.File]::WriteAllText(($source + '.meta'), "fileFormatVersion: 2`nguid: 22222222222222222222222222222222`nfolderAsset: yes`n")
        $before = Get-YamyamTerrainInventory $source $fixture
        switch ($case) {
            'dry-apply' {
                $dry = Invoke-YamyamTerrainRetirement $fixture $false '' ''
                Assert-True ($dry.status -eq 'ready-dry-run' -and (Test-Path -LiteralPath $source)) 'Dry-run changed generated source'
                Assert-True ($dry.bytes -gt $before.inventory.folderMeta.bytes) 'Inventory summary omitted payload bytes'
                $result = Invoke-YamyamTerrainRetirement $fixture $true $dry.inventorySha256 $dry.manifestSha256
                Assert-True ($result.status -eq 'retired' -and -not (Test-Path -LiteralPath $source)) 'Apply did not retire exact tree'
                Assert-True ((Get-YamyamTerrainInventory $result.destination $fixture).inventorySha256 -eq $before.inventorySha256) 'Moved GUID/payload inventory changed'
                Assert-True ((Get-YamyamTerrainInventory $result.originalBackup $fixture).inventorySha256 -eq $before.inventorySha256) 'Independent original backup missing'
                $again = Invoke-YamyamTerrainRetirement $fixture $true '' ''
                Assert-True ($again.status -eq 'retired') 'Completed retirement resume failed'
                New-Item -ItemType Directory -Path $source -Force | Out-Null
                Assert-Throws { Invoke-YamyamTerrainRetirement $fixture $true '' '' }
            }
            'active' {
                $script:FixtureProcesses = @([pscustomobject]@{ ProcessId = 123; ExecutablePath = 'C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe'; CommandLine = "Unity.exe -projectPath `"$headless`"" })
                Assert-Throws { Invoke-YamyamTerrainRetirement $fixture $true '' '' }
                $script:FixtureProcesses = @([pscustomobject]@{ ProcessId = 456; ExecutablePath = 'C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe'; CommandLine = "Unity.exe -projectPath `"$fixture`"" })
                Assert-YamyamNoIsolatedUnity $headless
                $main = $script:FixtureProcesses[0]
                $script:FixtureProcesses = @($main, [pscustomobject]@{ ProcessId = 457; ParentProcessId = 456; ExecutablePath = $main.ExecutablePath; CommandLine = 'Unity.exe --worker fixture' }, [pscustomobject]@{ ProcessId = 458; ParentProcessId = 457; ExecutablePath = $main.ExecutablePath; CommandLine = 'Unity.exe --worker nested' })
                Assert-YamyamNoIsolatedUnity $headless
                $main.CommandLine = "Unity.exe -projectPath `"$headless`""
                Assert-Throws { Assert-YamyamNoIsolatedUnity $headless }
                $main.CommandLine = 'Unity.exe --unknown-root'
                Assert-Throws { Assert-YamyamNoIsolatedUnity $headless }
                $script:FixtureProcesses = @([pscustomobject]@{ ProcessId = 789; ExecutablePath = 'C:\Program Files\Unity Hub\resources\unity.exe'; CommandLine = $null })
                Assert-YamyamNoIsolatedUnity $headless
                $script:FixtureProcesses = @([pscustomobject]@{ ProcessId = 790; ExecutablePath = 'C:\Other\Unity.exe'; CommandLine = "Unity.exe -projectPath `"$fixture`"" })
                Assert-Throws { Assert-YamyamNoIsolatedUnity $headless }
                $script:FixtureProcesses = @()
                Assert-True ((Get-YamyamTerrainInventory $source $fixture).inventorySha256 -eq $before.inventorySha256) 'Active guard mutated input'
            }
            'wrong-input' {
                Assert-Throws { Invoke-YamyamTerrainRetirement $fixture $true ('0' * 64) '' }
                Assert-Throws { Invoke-YamyamTerrainRetirement $fixture $true '' ('0' * 64) }
                Assert-Throws { Invoke-YamyamTerrainRetirement (Join-Path $fixture 'other') $true '' '' }
                Assert-True ((Get-YamyamTerrainInventory $source $fixture).inventorySha256 -eq $before.inventorySha256) 'Input refusal mutated source'
            }
            'rollback' {
                $script:MoveFault = 'directory'
                $result = Invoke-YamyamTerrainRetirement $fixture $true '' ''
                Assert-True ($result.status -eq 'failed' -and $result.rollbackComplete) 'Second rename failure did not roll back metadata'
                Assert-True ((Get-YamyamTerrainInventory $source $fixture).inventorySha256 -eq $before.inventorySha256) 'Rollback changed source GUID/payload'
            }
            'foreign' {
                $script:MoveFault = 'foreign'
                $result = Invoke-YamyamTerrainRetirement $fixture $true '' ''
                Assert-True ($result.status -eq 'failed' -and -not $result.rollbackComplete) 'Foreign write was incorrectly overwritten'
                Assert-True ([IO.File]::ReadAllText((Join-Path $result.destination 'one.terrainlayer')) -eq 'newer foreign data') 'Foreign bytes lost'
                Assert-True ((Get-YamyamTerrainInventory $result.originalBackup $fixture).inventorySha256 -eq $before.inventorySha256) 'Original backup lost after foreign write'
            }
            'reparse' {
                $target = Join-Path $fixture 'elsewhere'; New-Item -ItemType Directory -Path $target | Out-Null
                $link = Join-Path $source 'unsafe-link'
                New-Item -ItemType Junction -Path $link -Target $target | Out-Null
                Assert-Throws { Invoke-YamyamTerrainRetirement $fixture $true '' '' }
                Remove-Item -LiteralPath $link -Force
            }
        }
        $passed++
    }
    "PASS: $passed temporary retirement fixture groups; no Unity process launched or stopped."
}
finally {
    $resolved = [IO.Path]::GetFullPath($temporaryBase)
    if (-not $resolved.StartsWith([IO.Path]::GetFullPath([IO.Path]::GetTempPath()), [StringComparison]::OrdinalIgnoreCase) -or -not (Split-Path -Leaf $resolved).StartsWith('yamyam-terrain-retirement-tests-')) { throw 'Unsafe fixture cleanup path' }
    Remove-Item -LiteralPath $resolved -Recurse -Force
}
