"""Use one timed pass of publisher-provided gameplay GIFs; never repeat a cycle."""
from pathlib import Path
import zipfile, subprocess, json, hashlib
from PIL import Image, ImageSequence
ROOT=Path(__file__).resolve().parents[3]
source=Path('C:/Users/eazuo/Downloads/IntoTheBreach_AdvancedEdition_PressKit.zip')
out=ROOT/'shared/assets/deconstruct-analyze-rebuild/raw/advanced-press-actions'
out.mkdir(parents=True,exist_ok=True)
names=['enemy combo','squad arachnophile combo','squad bombermechs combo','squad cataclysm combo','squad heatsinkers combo','squad misteaters combo','weapon bounceshot','combat volcanofall']
records=[]
with zipfile.ZipFile(source) as z:
 for name in names:
  entry=f'Press Kit/gifs/{name}.gif'
  # Write only these exact entries; no extracted archive paths are trusted.
  gif=out/(name.replace(' ','-')+'.gif')
  data=z.read(entry); gif.write_bytes(data)
  with Image.open(gif) as im:
   ms=[f.info.get('duration',0) for f in ImageSequence.Iterator(im)]
   if any(d<=0 for d in ms): raise ValueError('GIF timing missing')
   seconds=sum(ms)/1000
   dimensions=im.size
  target=gif.with_suffix('.mp4')
  subprocess.run(['ffmpeg','-v','error','-y','-ignore_loop','1','-i',str(gif),'-an','-vf','fps=60,scale=1920:1080:flags=neighbor,setsar=1','-t',str(seconds),'-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000',str(target)],check=True)
  records.append({'key':'breach-'+name.replace(' ','-'),'file':str(target.relative_to(ROOT)).replace('\\','/'),'originalGif':str(gif.relative_to(ROOT)).replace('\\','/'),'sourceArchive':'https://subsetgames.com/presskit/IntoTheBreach_AdvancedEdition_PressKit.zip','archiveEntry':entry,'publisher':'Subset Games','gifSha256':hashlib.sha256(data).hexdigest(),'nativeDurationSeconds':seconds,'nativeFrames':len(ms),'nativeSize':dimensions,'conversion':'one original-timed GIF pass to60fps; ignore_loop=1; no loop/slowdown/end hold','status':'decoded-awaiting-direct-action-review'})
(ROOT/'projects/deconstruct-analyze-rebuild/sources/breach-advanced-actions.json').write_text(json.dumps({'archiveSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'files':records},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(records,ensure_ascii=False))
