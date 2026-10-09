"""Rebuild final QA; compare directly viewed baseline pixels, then stop for review."""
from pathlib import Path
import subprocess,sys,json,hashlib,math
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent;slug='game-math-normal-transform-uv'
W=R/'shared/output'/slug;Q=W/'qa';P=R/'projects'/slug/'production'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for script,args in [('build.py',[slug,'burn']),('build.py',[slug,'qa']),('inspect-final-beats.py',[slug]),('inspect-final-observations.py',[slug]),('research/verify-normal-transform-uv.py',[])]:
 log=W/('subject-repair-'+Path(script).stem+'-'+(args[-1] if args else 'math')+'.log')
 print('Starting',script,*args,flush=True)
 with log.open('w',encoding='utf8') as f:subprocess.run([sys.executable,'-X','utf8',str(B/script),*args],cwd=R,stdout=f,stderr=subprocess.STDOUT,check=True)
 print('Completed',script,*args,flush=True)
old=read(W/'before-subject-timing-repair/prior-direct-pixel-review.json');qa=read(P/'qa.json');beats=read(Q/'final-beats/generated-samples.json');ob=read(Q/'observation-samples.json')
assert qa['fullDecodePassed'] and qa['videos']['videoBurnedCaptions']['sha256']==beats['videoSha256']==ob['videoSha256']!=old['videoSha256']
images=sorted(Q.glob('caption-strips-*.jpg'))+sorted(Q.glob('composition-sheet-*.jpg'))+[R/x['path'] for x in beats['records']]+[R/x['path'] for x in ob['sheets']]
same=[];changed=[]
for p in images:
 relative=p.relative_to(R).as_posix();previous=next((x for x in old['images'] if x['path']==relative),None)
 (same if previous and sha(p)==previous['sha256'] else changed).append(relative)
value=dict(oldReview='shared/output/'+slug+'/before-subject-timing-repair/prior-direct-pixel-review.json',currentVideoSha256=beats['videoSha256'],identicalPixelSheets=same,requiresFreshDirectView=changed,status='comparison-only-direct-view-pending')
write(Q/'subject-repair-image-comparison.json',value)
t=read(P/'timeline.json');s=next(x for x in t['scenes'] if x['id']=='08');v=R/qa['videos']['videoBurnedCaptions']['path']
times=[]
for i in [1,2,3,4]:
 at=s['cuts'][i]['outputStart'];times.extend([dict(time=at-1/60,label=f'cut{i} last prior frame'),dict(time=at+1/60,label=f'cut{i} first next frame')])
for i,label in [(87,'roof sentence88'),(88,'container sentence89')]:
 c=t['koCaptions'][i];times.append(dict(time=c['start']+min(1.5,(c['end']-c['start'])/2),label=label))
times.sort(key=lambda x:x['time']);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);sheets=[]
for page in range(math.ceil(len(times)/4)):
 group=times[page*4:(page+1)*4];sheet=Image.new('RGB',(1920,1160),'#e9edf0');draw=ImageDraw.Draw(sheet)
 for j,x in enumerate(group):
  f=Q/f'subject-boundary-{page*4+j+1:02}.jpg'
  subprocess.run(['ffmpeg','-v','error','-y','-ss',str(x['time']),'-threads','4','-i',str(v),'-frames:v','1','-vf','scale=960:540','-threads','4',str(f)],check=True)
  left=(j%2)*960;top=(j//2)*580;draw.text((left+8,top+6),f"{x['label']} / {x['time']:.3f}s",fill='black',font=font);sheet.paste(Image.open(f),(left,top+30))
 p=Q/f'subject-boundary-sheet-{page+1:02}.jpg';sheet.save(p,quality=95);sheets.append(dict(path=p.relative_to(R).as_posix(),sha256=sha(p)))
write(Q/'subject-boundary-samples.json',dict(status='generated-pending-direct-view',videoSha256=sha(v),samples=times,sheets=sheets))
print(json.dumps(dict(identical=len(same),requiresFreshDirectView=changed,extraBoundarySheets=sheets,actionSamples=len(ob['samples']),totalSheets=len(images)),ensure_ascii=False),flush=True)
