"""Read new normal-speed flight positions from an already compiled native cut."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os,subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
dest=BASE/'measured-edit-v4/rocket-flight-context-local';assert not dest.exists();dest.mkdir()
cut=next(c for c in read(BASE/'measured-edit-v4/native-review-v1/compiled.json')['cuts'] if c['id']=='06-p5-action-64-4860-5270')
video=ROOT/cut['video'];assert sha(video)==cut['sha256']
native=[4960,4970,4980,4990,5000,5030,5060,5090,5100,5130,5160,5190]
vf="select='"+'+'.join(f'eq(n\\,{n-4860})' for n in native)+"'"
cmd=['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-v','error','-threads','2','-i',str(video),'-vf',vf,'-fps_mode','passthrough','-frames:v',str(len(native)),str(dest/'frame-%03d.png')]
state={'pid':os.getpid(),'startedAt':datetime.now(timezone.utc).isoformat(),'status':'CPU-new-flight-boundary-context','sourceCut':cut,'newGitImages':0,'frames':native,'command':cmd}
with (dest/'extract.log').open('wb') as fh:
 p=subprocess.Popen(cmd,stdout=fh,stderr=fh,creationflags=subprocess.CREATE_NO_WINDOW);state['childPid']=p.pid
 (dest/'execution.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8');code=p.wait()
assert code==0 and not (dest/'extract.log').read_text().strip()
state['images']=[{'nativeFrame':n,'path':rel(f),'sha256':sha(f),'directlyRead':False} for n,f in zip(native,sorted(dest.glob('frame-*.png')))]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',26);state['sheets']=[]
for off in range(0,12,6):
 im=Image.new('RGB',(1920,1740),'white');d=ImageDraw.Draw(im)
 for k,r in enumerate(state['images'][off:off+6]):
  x,y=(k%2)*960,(k//2)*580
  with Image.open(ROOT/r['path']) as a:im.paste(a.resize((960,540)),(x,y+40))
  d.text((x+8,y+5),f"native{r['nativeFrame']} / Rocket Ride",font=font,fill='black')
 out=dest/f'sheet-{off//6+1}.jpg';im.save(out,quality=95);state['sheets'].append({'path':rel(out),'sha256':sha(out)})
state.update(endedAt=datetime.now(timezone.utc).isoformat(),status='closed-new-flight-context-awaiting-read',exitCode=code)
(dest/'execution.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pid':os.getpid(),'childPid':p.pid,'exitCode':code,'images':12,'sheets':2}))
