// Export the finalized editable deck through installed PowerPoint, without a window.
// Close only this read-only document; never close the user's open presentations.
const {spawnSync}=require('node:child_process');
const [source,directory]=process.argv.slice(2);
if(!source||!directory)throw Error('Usage: render-tool-slides.cjs <pptx> <private output>');
const quote=s=>"'"+s.replace(/'/g,"''")+"'";
const script=`$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
$previous=Get-Process POWERPNT -ErrorAction SilentlyContinue
$app=New-Object -ComObject PowerPoint.Application
$deck=$null
try {
 $deck=$app.Presentations.Open(${quote(source)},-1,0,0)
 for($i=1;$i -le $deck.Slides.Count;$i++) {
  $target=Join-Path ${quote(directory)} ('slide-{0:D2}.png' -f $i)
  $deck.Slides.Item($i).Export($target,'PNG',1920,1080)
 }
 Write-Output ('Exported {0} slides from final PPTX' -f $deck.Slides.Count)
} finally {
 if($null -ne $deck){$deck.Close();[void][Runtime.InteropServices.Marshal]::ReleaseComObject($deck)}
 if(!$previous -and $app.Presentations.Count -eq 0){$app.Quit()}
 [void][Runtime.InteropServices.Marshal]::ReleaseComObject($app)
}`;
const result=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-EncodedCommand',Buffer.from(script,'utf16le').toString('base64')],{encoding:'utf8',windowsHide:true});
process.stdout.write(result.stdout||'');process.stderr.write(result.stderr||'');
if(result.status!==0)process.exit(result.status||1);
