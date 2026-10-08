"""Plan or extract current final encoded cue/cut/paragraph pixels; no approval."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, math, os, subprocess, sys, time, traceback
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
DEST=ROOT/'shared/output/player-customization/final-encoded-caption-qa-v1'
STATE=W/'encoded-caption-qa-execution.json';SESSION=W/'encoded-caption-qa-session.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing')
 for n in range(60):
  try:t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p);return
  except OSError:
   if n==59:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--plan-only',action='store_true');ap.add_argument('--resource');a=ap.parse_args()
plan=read(W/'plan.json');captions=read(ROOT/plan['captionSource']);timing=read(ROOT/plan['voiceTiming'])
assert sha(ROOT/plan['captionSource'])==plan['captionSourceSha256'] and len(captions['ko'])==415 and len(captions['en'])==162
assert sha(ROOT/plan['voiceTiming'])==plan['voiceTimingSha256']
segments=[dict(id='branding',startFrame=0,frames=120,role='branding')]
segments += [dict(id=f'{k:03d}-{c["scene"]}-p{c["paragraph"]}',startFrame=c['outputStartFrame'],frames=c['frames'],role=c['role'],scene=c['scene'],paragraph=c['paragraph'],sourceKey=c.get('sourceKey')) for k,c in enumerate(plan['cuts'],1)]
segments.append(dict(id='membership',startFrame=35441,frames=600,role='membership'))
def ass_time(s):
 h,m,z=s.split(':');return int(h)*3600+int(m)*60+float(z)
assCues=[]
for line in (W/'captions.ko.ass').read_text('utf-8-sig').splitlines():
 if line.startswith('Dialogue: 2,'):
  parts=line.split(',',9);assCues.append(dict(index=len(assCues)+1,startSeconds=ass_time(parts[1]),endSeconds=ass_time(parts[2])))
assert len(assCues)==415
for row,c in zip(captions['ko'],assCues):assert abs(row['startSeconds']-c['startSeconds'])<=.011 and abs(row['endSeconds']-c['endSeconds'])<=.011
points={}
def add(f,reason,cue=None):
 f=int(f)
 if 0<=f<36041:
  row=points.setdefault(f,dict(frame=f,anchors=[],cueIds=[]))
  if reason not in row['anchors']:row['anchors'].append(reason)
  if cue is not None and cue not in row['cueIds']:row['cueIds'].append(cue)
for cue in assCues:
 lo=math.ceil(cue['startSeconds']*60-1e-7);hi=math.ceil(cue['endSeconds']*60-1e-7)
 assert hi>lo
 for f,label in [(lo,'cue-first'),((lo+hi-1)//2,'cue-mid'),(hi-1,'cue-last')]:add(f,f'{label}:{cue["index"]}',cue['index'])
 for seg in segments:
  x,y=max(lo,seg['startFrame']),min(hi,seg['startFrame']+seg['frames'])
  if y>x:add((x+y-1)//2,f'cue/segment:{seg["id"]}',cue['index'])
for seg in segments:
 lo=seg['startFrame'];hi=lo+seg['frames']
 for f,label in [(lo-1,'before-cut'),(lo,'first-cut'),((lo+hi-1)//2,'mid-cut'),(hi-1,'last-cut'),(hi,'after-cut')]:add(f,f'{label}:{seg["id"]}')
 if seg['role']=='explanation':
  for fraction in [.25,.75]:add(lo+int((hi-lo-1)*fraction),f'white-motion:{seg["id"]}')
for scene in timing['rows']:
 for p,sample in enumerate(scene['paragraphStartSamples'],1):
  f=scene['startFrame']+round(sample/400)
  for offset in [-1,0,1]:add(f+offset,f'PCM-onset:{scene["id"]}p{p}')
# Exact repaired action clauses get dense final samples, including all source edits.
historicalRepair=read(ROOT/plan['priorCandidate'])
repairIntervals={(c['outputStartFrame'],c['outputStartFrame']+c['frames']) for c in [*historicalRepair['cuts'],*plan['cuts']] if c.get('repairNativeOnly')}
for lo,hi in sorted(repairIntervals):
 for f in range(lo,hi,15):add(f,'dense-repaired-action')
for f in [0,60,119,120,1445,35440,35441,35501,35741,35981,36040]:add(f,'branding/overview/member-identity-edge')
for f,row in points.items():
 seg=next(s for s in segments if s['startFrame']<=f<s['startFrame']+s['frames'])
 row.update(segment=seg['id'],role=seg['role'],scene=seg.get('scene'),paragraph=seg.get('paragraph'),sourceKey=seg.get('sourceKey'),seconds=f/60)
 row['visibleCueIds']=[c['index'] for c in assCues if c['startSeconds']<=f/60+1e-7<c['endSeconds']]
assert {c for row in points.values() for c in row['cueIds']}==set(range(1,416))
request=dict(createdAt=now(),planSha256=sha(W/'plan.json'),captionAssSha256=sha(W/'captions.ko.ass'),captionSourceSha256=plan['captionSourceSha256'],
 frames=36041,sampledFrames=len(points),koCueCount=415,enCueCount=162,cutCount=139,actualCutCount=sum(s['role']=='actual-game' for s in segments),
 whiteCutCount=sum(s['role']=='explanation' for s in segments),all64PcmOnsetsCovered=True,allCueCutIntersectionsCovered=True,
 points=[points[f] for f in sorted(points)],imagesLocalOnly=True,newGitImages=0,allFinalPixels=False)
save(W/'encoded-caption-qa-request.json',request)
if a.plan_only:
 print(json.dumps(dict(plannedFrames=len(points),boards=math.ceil(len(points)/6),koCues=415,cuts=139,actualImagesCreated=0,allFinalPixels=False)));sys.exit(0)
assert a.resource
r=read(ROOT/a.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'].replace('Z','+00:00'))).total_seconds()<240
pair=read(W/'review-pair-build.json');assert pair['planSha256']==request['planSha256'] and pair['captionAssSha256']==request['captionAssSha256'] and pair['identicalAacPayload']
assert read(W/'review-pair-execution.json')['exitCode']==0
record=next(x for x in pair['records'] if '.captioned.' in x['path']);source=ROOT/record['path'];assert sha(source)==record['sha256']
assert not STATE.exists() and not DEST.exists(),'Read actual extraction checkpoint; never repeat completed frames.'
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
DEST.mkdir();(DEST/'frames').mkdir();(DEST/'boards').mkdir()
s=dict(schemaVersion=1,slug='player-customization',pid=os.getpid(),sessionId=None,commandLine=[sys.executable,*sys.argv],startedAt=now(),
 status='extracting-current-final-encoded-pixels',resourceEvidence=a.resource,cpuThreads=2,gpu=0,singleJob=True,exitCode=None,activeTask=None,
 source=rel(source),sourceSha256=record['sha256'],requestPath=rel(W/'encoded-caption-qa-request.json'),requestSha256=sha(W/'encoded-caption-qa-request.json'),
 samples=[],boards=[],allFinalPixels=False,qaApproved=False,collected=False,uploaded=False,imagesLocalOnly=True,newGitImages=0)
def checkpoint():
 if SESSION.exists():
  v=read(SESSION)
  if v['pid']==os.getpid():s.update(sessionId=v['sessionId'],processIdentity=v['processIdentity'])
 s['observedAt']=now();save(STATE,s)
 job=dict(pid=s['pid'],sessionId=s['sessionId'],processIdentity=s.get('processIdentity'),commandLine=s['commandLine'],state=rel(STATE),status=s['status'],
  cpuThreads=2,gpu=0,singleJob=True,activeTask=s['activeTask'],exitCode=s['exitCode'],workerExpectedRunning=s['exitCode'] is None)
 cpPath=BASE/'latest-checkpoint.json';cp=read(cpPath);cp.update(stage=s['status'],ownedJob=job,recordedAt=now(),encodedPixelExecution=rel(STATE),
  allFinalPixels=False,qaApproved=False,collected=False,uploaded=False,nextAction='Directly read every current final board/cue/cut/PCM/white motion/member identity. Only then QA and4file collection/private settings/Git.');save(cpPath,cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items'] if x['slug']=='player-customization')
 i.update(stage=s['status'],currentExecution=job,encodedPixelExecution=rel(STATE),allFinalPixels=False,qaApproved=False,collected=False,uploaded=False,nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
try:
 checkpoint();expr="select='"+'+'.join(f'eq(n,{f})' for f in sorted(points))+"'"
 cmd=[str(FF),'-v','error','-nostdin','-threads','2','-i',str(source),'-an','-filter_threads','1','-vf',expr,'-fps_mode','passthrough','-frames:v',str(len(points)),'-threads','2',str(DEST/'frames/frame-%04d.png')]
 log=DEST/'extract.log'
 with log.open('w',encoding='utf-8') as stream:
  child=subprocess.Popen(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);s['activeTask']=dict(pid=child.pid,commandLine=cmd,log=rel(log));checkpoint();code=child.wait()
 assert code==0 and not log.read_text('utf-8-sig').strip(),(code,rel(log))
 files=sorted((DEST/'frames').glob('frame-*.png'));assert len(files)==len(points)
 for index,(path,f) in enumerate(zip(files,sorted(points)),1):s['samples'].append(dict(index=index,**points[f],path=rel(path),sha256=sha(path),directlyRead=False))
 s.update(status='creating-current-final-review-boards',activeTask=None);checkpoint();font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
 for offset in range(0,len(files),6):
  rows=s['samples'][offset:offset+6];board=Image.new('RGB',(1920,1740),'white');draw=ImageDraw.Draw(board)
  for slot,row in enumerate(rows):
   x,y=slot%2*960,slot//2*580
   with Image.open(ROOT/row['path']) as im:assert im.size==(1920,1080);board.paste(im.resize((960,540)),(x,y+40))
   draw.text((x+5,y+4),f'{row["index"]:04d} n{row["frame"]} {row["segment"][:35]} cue{row["visibleCueIds"]}',font=font,fill='black')
  path=DEST/f'boards/board-{offset//6+1:03d}.png';board.save(path)
  s['boards'].append(dict(index=offset//6+1,path=rel(path),sha256=sha(path),sampleIndices=[r['index'] for r in rows],directlyRead=False))
 s.update(status='closed-current-final-pixels-awaiting-full-direct-review',exitCode=0,endedAt=now(),activeTask=None,sampleCount=len(s['samples']),boardCount=len(s['boards']));checkpoint()
 print(json.dumps(dict(exitCode=0,frames=len(files),boards=len(s['boards']),allFinalPixels=False,newGitImages=0)),flush=True)
except BaseException:
 s.update(status='closed-current-final-pixel-extraction-failed',exitCode=1,endedAt=now(),activeTask=None,error=traceback.format_exc());checkpoint();raise
