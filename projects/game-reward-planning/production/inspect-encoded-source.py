"""Capture first/middle/last frames of the67 already compiled review clips."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'measured-edit-v2/source-review-v1';DEST=WORK/'encoded-boundaries-v2';DEST.mkdir(exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf8'));now=lambda:datetime.now(timezone.utc).isoformat();FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
compiled=read(WORK/'compiled.json');state={'pid':os.getpid(),'startedAt':now(),'status':'running','gpuJobs':0,'completed':[],'children':[],'finalApproved':False}
def save():state['updatedAt']=now();(DEST/'execution.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
save();rows=[]
for c in compiled['cuts']:
 points=[0,c['frames']//2,c['frames']-1];folder=DEST/c['id'];folder.mkdir();vf="select='"+'+'.join('eq(n\\,%d)'%n for n in points)+"'"
 args=[FF,'-v','error','-threads','2','-i',str(ROOT/c['video']),'-vf',vf,'-fps_mode','vfr','-q:v','2',str(folder/'frame-%02d.jpg')]
 with (folder/'extract.log').open('w') as log:
  p=subprocess.Popen(args,stdout=log,stderr=log);state['activeChild']={'pid':p.pid,'id':c['id'],'command':args};save();code=p.wait();state['children'].append({'pid':p.pid,'id':c['id'],'exitCode':code});assert code==0
 files=sorted(folder.glob('frame-*.jpg'));assert len(files)==3
 for role,n,f in zip(['first','middle','last'],points,files):rows.append({'cut':c['id'],'scene':c['scene'],'sourceId':c['sourceId'],'role':role,'encodedFrame':n,'sourceSecond':c['sourceInSeconds']+n/60,'image':f.relative_to(ROOT).as_posix(),'directlyRead':False})
 state['completed'].append(c['id']);state['activeChild']=None;save()
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);pages=[]
for offset in range(0,len(rows),24):
 subset=rows[offset:offset+24];page=Image.new('RGB',(1920,6*300),'#eeeeee');d=ImageDraw.Draw(page)
 for j,r in enumerate(subset):
  x=j%4*480;y=j//4*300;page.paste(Image.open(ROOT/r['image']).resize((480,270)),(x,y));d.text((x+5,y+272),f"{r['cut']} {r['role']} {r['sourceSecond']:.3f}s",font=font,fill='black')
 f=DEST/f'page-{len(pages)+1:02d}.jpg';page.save(f,quality=95);pages.append(f.relative_to(ROOT).as_posix())
(DEST/'index.json').write_text(json.dumps({'status':'encoded-source-boundaries-awaiting-direct-reading','rows':rows,'pages':pages,'compiledSha256':hashlib.sha256((WORK/'compiled.json').read_bytes()).hexdigest(),'allCaptionPixelsApproved':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8');state.update(status='finished-awaiting-direct-reading',exitCode=0,endedAt=now());save();print(json.dumps({'frames':len(rows),'pages':len(pages)}))
