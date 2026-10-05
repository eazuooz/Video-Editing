"""Sample every current framed cut and every intersecting fixed Korean cue.

These are new encoded framing/word-aligned candidate pixels, retained locally.
"""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,os,subprocess,time,traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'measured-edit-v6';DEST=WORK/'current-framed-cue-local'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.writing')
 for n in range(30):
  try:t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p);return
  except OSError:
   if n==29:raise
   time.sleep(.1)
assert not DEST.exists();DEST.mkdir()
media=read(WORK/'framed-media-index.json');layout=read(WORK/'caption-layout-v1.json');plan=read(WORK/'plan.json')
assert len(media['cuts'])==111 and layout['cueCount']==199 and plan['finalFrames']==32100
state=dict(startedAt=now(),pid=os.getpid(),sessionId=None,status='CPU-current-encoded-framed-cue-extraction',activeTasks=[],images=[],sheets=[],completedCuts=0,
 planSha256=sha(WORK/'plan.json'),mediaIndexSha256=sha(WORK/'framed-media-index.json'),captionLayoutSha256=sha(WORK/'caption-layout-v1.json'),
 fixedCaptionCenter=[960,970],newGitImages=0,allFinalPixelsApproved=False)
def save():
 ss=DEST/'session.json'
 if ss.exists():state['sessionId']=read(ss)['sessionId']
 write(DEST/'execution.json',state)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='avoid-game-comparisons')
 item.update(stage='current15-v6-current-encoded-cue-pixel-review',updatedAt=now(),nextAction='Read every current framed/caption intersection and timed white reel; then synchronize final timing, mix and final QA. Preserve current PCM and all completed work.')
 item['execution'].update(observedAt=now(),phase=item['stage'],status=state['status'],pid=os.getpid(),sessionId=state['sessionId'],alive='endedAt' not in state,
  activeTasks=state['activeTasks'],cpuProductionJobs=0 if 'endedAt' in state else 1,gpuSynthesisJobs=0,uploads=0,state=rel(DEST/'execution.json'))
 q['updatedAt']=now();write(qp,q)
 for p in [BASE/'latest-checkpoint.json',ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/latest-checkpoint.json']:
  d=read(p)
  for k in ['stage','execution','updatedAt','nextAction']:d[k]=item[k]
  write(p,d)
try:
 save()
 for cut in media['cuts']:
  assert sha(ROOT/cut['video'])==cut['sha256']
  points={0:{'anchors':['first'],'cues':[]},cut['frames']//2:{'anchors':['middle'],'cues':[]},cut['frames']-1:{'anchors':['last'],'cues':[]}}
  for row in layout['rows']:
   if row['segment']==cut['id']:points.setdefault(row['localFrame'],dict(anchors=[],cues=[]))['cues'].append(row['cue'])
  if cut['id'] in ['02-p4-action-21-1410-1455','06-p2-action-31-900-945']:
   for n in range(0,cut['frames'],3):points.setdefault(n,dict(anchors=['dense-dynamic-motion'],cues=[]))
  folder=DEST/cut['id'];folder.mkdir();select='+'.join(f'eq(n\\,{n})' for n in sorted(points))
  vf=f"setpts=PTS+{cut['startFrame']/60:.9f}/TB,subtitles=captions.ko.candidate.ass,select='{select}'"
  log=folder/'extract.log'
  with log.open('wb') as f:
   child=subprocess.Popen(['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-v','error','-nostdin','-threads','2','-i',str(ROOT/cut['video']),'-vf',vf,'-fps_mode','passthrough','-frames:v',str(len(points)),str(folder/'sample-%03d.png')],cwd=WORK,stdout=f,stderr=f,creationflags=subprocess.CREATE_NO_WINDOW)
   state['activeTasks']=[dict(kind='CPU-current-caption-pixels',pid=child.pid,log=rel(log))];save();code=child.wait()
  state['activeTasks']=[];assert code==0 and not log.read_text().strip()
  files=sorted(folder.glob('sample-*.png'));assert len(files)==len(points)
  for file,n in zip(files,sorted(points)):
   state['images'].append(dict(path=rel(file),sha256=sha(file),cut=cut['id'],localFrame=n,globalFrame=cut['startFrame']+n,
    cueIds=points[n]['cues'],anchorRoles=points[n]['anchors'],directlyRead=False,finalApproved=False))
  state['completedCuts']+=1;save();print(f'Pixels {state["completedCuts"]}/111',flush=True)
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
 for off in range(0,len(state['images']),6):
  subset=state['images'][off:off+6];img=Image.new('RGB',(1920,1740),'white');draw=ImageDraw.Draw(img)
  for k,row in enumerate(subset):
   x,y=k%2*960,k//2*580
   with Image.open(ROOT/row['path']) as raw:img.paste(raw.resize((960,540)),(x,y+40))
   draw.text((x+7,y+7),f'{off+k+1:03d} {row["cut"]} n{row["localFrame"]} cue{row["cueIds"]}',font=font,fill='black')
  out=DEST/f'review-sheet-{off//6+1:03d}.jpg';img.save(out,quality=94)
  state['sheets'].append(dict(path=rel(out),sha256=sha(out),imageIndices=list(range(off+1,off+len(subset)+1)),directlyRead=False))
 state.update(status='closed-current111-framed-cues-awaiting-direct-read',endedAt=now(),exitCode=0);save()
 print(json.dumps(dict(images=len(state['images']),sheets=len(state['sheets']),cuts=111)))
except BaseException:
 state.update(status='closed-current-framed-cue-extraction-failed',endedAt=now(),exitCode=1,error=traceback.format_exc(),activeTasks=[]);save();raise
