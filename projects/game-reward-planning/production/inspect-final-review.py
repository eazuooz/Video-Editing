"""Every caption/cut intersection and encoded cut boundary, from rendered pixels."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'final-v1';DEST=WORK/'pixel-review-v1';DEST.mkdir(exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();now=lambda:datetime.now(timezone.utc).isoformat();FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
result=read(WORK/'render-result.json');file=ROOT/result['captioned'];assert sha(file)==result['captionedSha256'];layout=read(BASE/'measured-edit-v3/caption-layout-qa.json');visual=read(WORK/'visual-build.json');rows=[{'kind':'caption-intersection','frame':r['sampleFrame'],'cue':r['cue'],'scene':r['scene'],'cut':r['segment'],'caption':r['lines']} for r in layout['rows']]
for s in visual['segments']:
 for label,n in [('first',s['startFrame']),('last',s['startFrame']+s['frames']-1)]:rows.append({'kind':'encoded-boundary','cut':s['id'],'frame':n,'phase':label})
for label,n in [('opening-full',600),('members-mid',result['frames']-300),('members-last',result['frames']-1)]:rows.append({'kind':'composition','label':label,'frame':n})
points=sorted(set(r['frame'] for r in rows));state={'pid':os.getpid(),'status':'running','startedAt':now(),'imagePoints':len(points),'rows':len(rows),'captionedSha256':sha(file),'automaticApproval':False}
def save():state['updatedAt']=now();(DEST/'execution.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
save();vf="select='"+'+'.join('eq(n\\,%d)'%n for n in points)+"'";args=[FF,'-v','error','-threads','2','-i',str(file),'-vf',vf,'-fps_mode','vfr','-q:v','2',str(DEST/'frame-%04d.jpg')]
with (DEST/'extract.log').open('w') as log:
 p=subprocess.Popen(args,stdout=log,stderr=log);state['childPid']=p.pid;save();code=p.wait();assert code==0
images=sorted(DEST.glob('frame-*.jpg'));assert len(images)==len(points);mapping={n:f for n,f in zip(points,images)}
for r in rows:r.update(image=mapping[r['frame']].relative_to(ROOT).as_posix(),directlyRead=False)
rows.sort(key=lambda r:(r['frame'],r['kind']));font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);pages=[]
for offset in range(0,len(rows),24):
 page=Image.new('RGB',(1920,1800),'#eee');d=ImageDraw.Draw(page)
 for k,r in enumerate(rows[offset:offset+24]):
  x=k%4*480;y=k//4*300;page.paste(Image.open(ROOT/r['image']).resize((480,270)),(x,y));label=f"f{r['frame']} c{r.get('cue','-')} {r.get('cut',r.get('label',''))} {r.get('phase','')}";d.text((x+3,y+272),label,font=font,fill='black')
 f=DEST/f'page-{len(pages)+1:02d}.jpg';page.save(f,quality=97);pages.append(f.relative_to(ROOT).as_posix())
probe=json.loads(subprocess.check_output([FP,'-v','error','-show_streams','-show_format','-of','json',str(file)],text=True));record={'status':'rendered-pixels-awaiting-direct-reading','captionedSha256':sha(file),'layoutSha256':sha(BASE/'measured-edit-v3/caption-layout-qa.json'),'rows':rows,'pages':pages,'probe':probe,'allCaptionPixelsApproved':False};(DEST/'index.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');state.update(status='finished-awaiting-direct-reading',exitCode=0,endedAt=now());save();print(json.dumps({'captionIntersectionRows':len(layout['rows']),'allRows':len(rows),'uniqueFrames':len(points),'pages':len(pages)}))
