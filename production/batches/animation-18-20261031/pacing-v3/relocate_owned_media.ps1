param([Parameter(Mandatory=$true)][string[]]$Episodes)
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath('D:\Github\VideoEditing')
$storage=[IO.Path]::GetFullPath('C:\Users\1\Videos\YamyamCoding\VideoEditing\animation-pacing-v3')
$batch=Join-Path $repo 'production\batches\animation-18-20261031'
$records=(Get-Content (Join-Path $batch 'real-clips-v2\review-manifest.json') -Raw|ConvertFrom-Json).records
$active=Get-Content (Join-Path $batch 'local\pacing-v3\active-job.json') -Raw|ConvertFrom-Json
$receiptPath=Join-Path $batch 'local\pacing-v3\storage-relocation.json'
$receipts=@()
if(Test-Path -LiteralPath $receiptPath){$receipts=@(Get-Content -LiteralPath $receiptPath -Raw|ConvertFrom-Json)}
New-Item -ItemType Directory -Path $storage -Force|Out-Null
foreach($ep in $Episodes){
 if($ep -eq 'A02' -or $ep -eq $active.episode){throw "Cannot relocate platform-bound or active episode $ep"}
 $row=@($records|Where-Object id -eq $ep);if($row.Count -ne 1){throw 'Unknown episode'}
 $slug=$row[0].slug
 $source=[IO.Path]::GetFullPath((Join-Path $repo "projects\$slug\production\local\pacing-v3"))
 $target=[IO.Path]::GetFullPath((Join-Path $storage $slug))
 if(!$source.StartsWith($repo+'\projects\') -or !( $source.EndsWith('\production\local\pacing-v3')) -or !$target.StartsWith($storage+'\')){throw 'Outside expected task-owned storage'}
 $item=Get-Item -LiteralPath $source
 if($item.Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Already linked: $source"}
 if(Test-Path -LiteralPath $target){throw "Target already exists: $target"}
 $manifest=Get-Content -LiteralPath (Join-Path $source "delivery\output\$slug\delivery-manifest.json") -Raw|ConvertFrom-Json
 if($manifest.revision -ne 'pacing-v3' -or !$manifest.narrationAllSamplesPreserved){throw 'Delivery not verified'}
 $before=@(Get-ChildItem -LiteralPath $source -Recurse -File|ForEach-Object { [pscustomobject]@{Relative=$_.FullName.Substring($source.Length+1);Length=$_.Length;Sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash} })
 # Only newly generated media for this finite revision, with resolved targets
 # verified above. Move and junction are both native PowerShell operations.
 Move-Item -LiteralPath $source -Destination $target
 New-Item -ItemType Junction -Path $source -Target $target|Out-Null
 foreach($file in $before){
  $p=Join-Path $source $file.Relative
  if((Get-Item -LiteralPath $p).Length -ne $file.Length -or (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash -ne $file.Sha256){throw "Relocation verification failed: $p"}
 }
 $receipts+=[pscustomobject]@{Episode=$ep;LogicalPath=$source;PhysicalPath=$target;Files=$before.Count;Bytes=($before|Measure-Object Length -Sum).Sum;AllFileHashesPreserved=$true;OldBaselinesMoved=$false;At=(Get-Date).ToUniversalTime().ToString('o')}
 $receipts|ConvertTo-Json -Depth 6|Set-Content -LiteralPath $receiptPath -Encoding utf8
 Write-Output "$ep relocated with all file hashes verified"
}
