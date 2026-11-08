from pathlib import Path
import json,subprocess,hashlib
from PIL import Image
P=Path(__file__).resolve().parents[1]; ROOT=P.parents[1]; A=P/'assets/local'
T=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-tools')
def run(args,cwd=None): subprocess.run([str(x) for x in args],cwd=cwd,check=True)
if not (A/'pixelfx-blue/fire/torch/torch.png').exists():
 run(['node','tools/render.mjs','fire/torch','--sheet','--no-actor','--fps','30','--scale','6','--opts',json.dumps({'palette':['#09294d','#145c8a','#2aaed4','#8ce8ed','#e8ffff']}),'--out',A/'pixelfx-blue'],T/'pixelfx')
baseline=ROOT/'projects/animation-assigning/production/local/pacing-v3/delivery/output/animation-assigning/animation-assigning.clean.mp4'
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(baseline)],text=True))
for name,start,length in [('intro',0,2),('outro',duration-10,10)]:
 dest=A/(name+'.mp4')
 if not dest.exists(): run(['ffmpeg','-hide_banner','-loglevel','error','-ss',start,'-i',baseline,'-t',length,'-an','-r','60','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',dest])
 snap=A/(name+'-review.jpg')
 if not snap.exists(): run(['ffmpeg','-hide_banner','-loglevel','error','-ss','1','-i',dest,'-frames:v','1',snap])
records=[]
for f in A.rglob('*.png'):
 if f.name.endswith('-review.png'): continue
 im=Image.open(f)
 rec={'path':f.relative_to(P).as_posix(),'size':list(im.size),'mode':im.mode,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
 if 'A' in im.getbands():
  h=im.getchannel('A').histogram();rec.update(alphaZero=h[0],alphaOpaque=h[255],alphaPartial=sum(h[1:255]))
 records.append(rec)
(P/'production/asset-inventory.json').write_text(json.dumps({'assets':records,'branding':{'source':baseline.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.file_digest(baseline.open('rb'),'sha256').hexdigest(),'sourceDuration':duration,'intro':[0,2],'outro':[duration-10,duration],'audio':'No original animation-series music retained in this lecture.'}},ensure_ascii=False,indent=2),encoding='utf-8')
for dirname in ('pixelfx','Pixelbolt'):
 for fn in ('LICENSE','LICENSE.md','NOTICE'):
  src=T/dirname/fn
  if src.exists():
   dst=P/'sources/licenses'/(dirname+'-'+fn+'.txt');dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(src.read_bytes())
print('Prepared',len(records),'image records and unchanged2s/10s branding')
