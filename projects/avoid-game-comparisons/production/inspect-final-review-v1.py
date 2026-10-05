"""Extract every current caption/cut intersection and encoded boundary for direct reading."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1';DEST=W/'pixel-review-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not DEST.exists();DEST.mkdir()
render=read(W/'render-result.json');video=ROOT/render['captioned'];assert sha(video)==render['captionedSha256'] and render['frames']==32100 and render['done'] and render['exactFramePts']['allFramePtsExact']
layout=read(BASE/'measured-edit-v6/caption-layout-v1.json');visual=read(W/'visual-build.json')
rows=[dict(kind='caption-intersection',frame=r['sampleFrame'],cue=r['cue'],scene=r['scene'],paragraph=r['paragraph'],cut=r['segment'],classification=r['classification'],caption=r['lines']) for r in layout['rows']]
assert len(rows)==278 and len(set(r['cue'] for r in rows))==199
for s in visual['segments']:
 for phase,n in [('first',s['startFrame']),('last',s['startFrame']+s['frames']-1)]:rows.append(dict(kind='encoded-boundary',cut=s['id'],frame=n,phase=phase,classification=s['classification']))
for label,n in [('overview-full',600),('membership-mid',31800),('membership-last',32099)]:rows.append(dict(kind='composition',label=label,frame=n))
points=sorted(set(r['frame'] for r in rows));assert min(points)==0 and max(points)==32099
state=dict(startedAt=now(),pid=os.getpid(),sessionId=None,status='extracting-current-final-rendered-pixels',captionedSha256=sha(video),rows=len(rows),imagePoints=len(points),newGitImages=0,automaticApproval=False)
write(DEST/'execution.json',state)
vf="select='"+'+'.join('eq(n\\,%d)'%n for n in points)+"'"
cmd=[FF,'-v','error','-threads','2','-reinit_filter','0','-i',str(video),'-vf',vf,'-fps_mode','passthrough','-q:v','2',str(DEST/'frame-%04d.jpg')]
with (DEST/'extract.log').open('w',encoding='utf-8') as log:
 p=subprocess.Popen(cmd,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW);state.update(childPid=p.pid,command=cmd);write(DEST/'execution.json',state);code=p.wait();assert code==0
images=sorted(DEST.glob('frame-*.jpg'));assert len(images)==len(points);mapping=dict(zip(points,images))
for r in rows:r.update(image=mapping[r['frame']].relative_to(ROOT).as_posix(),imageSha256=sha(mapping[r['frame']]),directlyRead=False)
rows.sort(key=lambda r:(r['frame'],r['kind']));font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20);pages=[]
for offset in range(0,len(rows),6):
 page=Image.new('RGB',(1920,1740),'#eee');d=ImageDraw.Draw(page)
 for k,r in enumerate(rows[offset:offset+6]):
  x=k%2*960;y=k//2*580;page.paste(Image.open(ROOT/r['image']).resize((960,540)),(x,y));label=f"f{r['frame']} c{r.get('cue','-')} {r.get('cut',r.get('label',''))} {r.get('phase','')}";d.text((x+4,y+544),label,font=font,fill='black')
 path=DEST/f'page-{len(pages)+1:03d}.jpg';page.save(path,quality=97);pages.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),rowFrom=offset,rowTo=min(offset+6,len(rows)),directlyRead=False))
write(DEST/'index.json',dict(status='current-rendered-pixels-awaiting-direct-reading',captionedSha256=render['captionedSha256'],layoutSha256=sha(BASE/'measured-edit-v6/caption-layout-v1.json'),visualBuildSha256=sha(W/'visual-build.json'),rows=rows,pages=pages,allCaptionPixelsApproved=False,localOnly=True,newGitImages=0))
state.update(status='closed-awaiting-direct-reading',exitCode=0,endedAt=now(),pages=len(pages));write(DEST/'execution.json',state);print(json.dumps(dict(rows=len(rows),uniqueFrames=len(points),pages=len(pages),all199KoreanCuesRepresented=True)))
