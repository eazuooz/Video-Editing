"""Plan or serially extract every current encoded cue/cut/PCM/motion anchor.

Plan-only creates no images. Extraction and pixel approval are separate.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,math,os,re,subprocess,time,traceback
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'revision-balatro60-v2/final-v3'
DEST=ROOT/'shared/output/presenting-game-scores/revision-balatro60-v2/final-encoded-caption-qa-v3'
STATE=W/'encoded-caption-qa-execution.json';SESSION=W/'encoded-caption-qa-session.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--plan-only',action='store_true');ap.add_argument('--resource');a=ap.parse_args()
plan=read(W/'plan.json');clock=read(W/'caption-clock-adoption.json');cap=read(W/'captions.json')
assert clock['finalAssSha256']==sha(W/'captions.ko.ass') and clock['captionJsonSha256']==sha(W/'captions.json')
assert (clock['koCueCount'],clock['enCueCount'],plan['finalFrames'])==(175,70,19988)
segments=[dict(id='branding',startFrame=0,frames=120,role='branding')]+plan['selectedInputSegments']+[dict(id='membership',startFrame=19388,frames=600,role='membership')]
assert len(segments)==33 and sum(s['frames']for s in segments)==19988
assert all(x['startFrame']+x['frames']==y['startFrame'] for x,y in zip(segments,segments[1:]))
def ass_seconds(t):
 h,m,s=t.split(':');return int(h)*3600+int(m)*60+float(s)
cues=[]
for line in (W/'captions.ko.ass').read_text('utf-8-sig').splitlines():
 if line.startswith('Dialogue: 2,'):
  fields=line.split(',',9);cues.append(dict(index=len(cues)+1,startSeconds=ass_seconds(fields[1]),endSeconds=ass_seconds(fields[2]),text=fields[9]))
assert len(cues)==175
points={}
def add(frame,anchor,cue=None):
 frame=int(frame)
 if 0<=frame<19988:
  row=points.setdefault(frame,dict(frame=frame,anchors=[],cueIds=[]))
  if anchor not in row['anchors']:row['anchors'].append(anchor)
  if cue is not None and cue not in row['cueIds']:row['cueIds'].append(cue)
for cue in cues:
 lo=math.ceil(cue['startSeconds']*60-1e-7);hi=math.ceil(cue['endSeconds']*60-1e-7);assert hi>lo
 for frame,label in [(lo,'cue-first'),((lo+hi-1)//2,'cue-mid'),(hi-1,'cue-last')]:add(frame,f'{label}:{cue["index"]}',cue['index'])
 for seg in segments:
  left=max(lo,seg['startFrame']);right=min(hi,seg['startFrame']+seg['frames'])
  if right>left:add((left+right-1)//2,f'cue/segment:{seg["id"]}',cue['index'])
for seg in segments:
 lo=seg['startFrame'];hi=lo+seg['frames']
 for frame,label in [(lo-1,'before-cut'),(lo,'first-cut'),(lo+1,'second-cut'),((lo+hi-1)//2,'mid-cut'),(hi-2,'penultimate-cut'),(hi-1,'last-cut'),(hi,'after-cut')]:add(frame,f'{label}:{seg["id"]}')
 if seg['role']=='explanation':
  for fraction in [.02,.18,.38,.60,.82,.97]:add(lo+round((hi-lo-1)*fraction),f'black-spatial-motion:{seg["id"]}:{fraction}')
for chunk in cap['chunks']:
 for edge,t in [('onset',chunk['startSeconds']),('end',chunk['endSeconds'])]:
  frame=math.ceil(t*60-1e-7)
  for offset in [-1,0,1]:add(frame+offset,f'complete-clause-{edge}:{chunk["scene"]}p{chunk["paragraph"]}c{chunk["chunk"]}')
for placement in plan['voicePlacements']:
 for edge,sample in [('onset',placement['startSample']),('end',placement['endSampleExclusive'])]:
  frame=math.ceil(sample/400)
  for offset in [-1,0,1]:add(frame+offset,f'PCM-placement-{edge}:{placement["id"]}')
preflight=read(ROOT/plan['selectedInputPreflight']);assert sha(ROOT/plan['selectedInputPreflight'])==plan['selectedInputPreflightSha256']
assert len(preflight['samples'])>0 and preflight['allSamplePtsVerified']
for sample in preflight['samples']:add(sample['frame']+120,f'approved-input-anchor:f{sample["frame"]}')
for frame in [0,60,119,120,1401,1402,19387,19388,19448,19688,19928,19987]:add(frame,'branding/overview/member-identity')
for frame,row in points.items():
 seg=next(x for x in segments if x['startFrame']<=frame<x['startFrame']+x['frames'])
 row.update(segment=seg['id'],role=seg['role'],chapter=seg.get('chapter'),source=seg.get('source'),seconds=frame/60,expectedPts=frame*1500,
  visibleCueIds=[c['index']for c in cues if c['startSeconds']<=frame/60+1e-7<c['endSeconds']])
assert {cue for row in points.values()for cue in row['cueIds']}==set(range(1,176))
request=dict(createdAt=now(),planSha256=sha(W/'plan.json'),captionAssSha256=sha(W/'captions.ko.ass'),frames=19988,
 sampledFrames=len(points),plannedBoards=math.ceil(len(points)/6),koCueCount=175,enCueCount=70,cutCount=31,
 actualCutCount=18,explanationCutCount=13,completeClauseOnsets=42,logicalParagraphs=39,pcmPlacements=len(plan['voicePlacements']),
 allCueCutIntersectionsCovered=True,allCurrentApprovedInputAnchorsRetained=True,points=[points[f]for f in sorted(points)],
 imagesLocalOnly=True,newGitImages=0,allFinalPixels=False,actualExtractionStarted=False)
request_path=W/'encoded-caption-qa-request.json'
if request_path.exists():
 prior=read(request_path);assert prior['planSha256']==request['planSha256'] and prior['captionAssSha256']==request['captionAssSha256']
 assert not prior['actualExtractionStarted'],'Read actual extraction checkpoint; never repeat.'
save(request_path,request)
if a.plan_only:
 print(json.dumps(dict(plannedFrames=len(points),plannedBoards=math.ceil(len(points)/6),koCues=175,cuts=31,clauses=42,actualImagesCreated=0,allFinalPixels=False)))
 raise SystemExit(0)
assert a.resource;r=read(ROOT/a.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
pair=read(W/'review-pair-build.json');execution=read(W/'review-pair-execution.json')
assert execution['exitCode']==execution['outerExitCode']==0 and execution['outerExitDirectlyObserved']
assert pair['planSha256']==request['planSha256'] and pair['captionAssSha256']==request['captionAssSha256'] and pair['identicalAacPayload']
record=next(x for x in pair['records']if '.captioned.' in x['path']);source=ROOT/record['path'];assert sha(source)==record['sha256']
assert not STATE.exists() and not DEST.exists(),'Resume actual extraction; no repeated frames.'
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
DEST.mkdir();(DEST/'frames').mkdir();(DEST/'boards').mkdir();p=psutil.Process()
s=dict(schemaVersion=1,slug='presenting-game-scores',pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),sessionId=None,
 startedAt=now(),status='extracting-current-final-encoded-pixels',resourceEvidence=a.resource,cpuThreads=2,gpu=0,singleJob=True,
 exitCode=None,activeTask=None,source=rel(source),sourceSha256=record['sha256'],requestPath=rel(request_path),
 requestSha256=sha(request_path),samples=[],boards=[],allFinalPixels=False,qaApproved=False,collected=False,uploaded=False,imagesLocalOnly=True,newGitImages=0)
def checkpoint():
 if SESSION.exists():
  x=read(SESSION)
  if x['pid']==s['pid'] and abs(x['createTime']-s['createTime'])<.01:s['sessionId']=x['sessionId']
 s['observedAt']=now();save(STATE,s)
 job=dict(pid=s['pid'],createTime=s['createTime'],command=s['command'],cwd=s['cwd'],sessionId=s['sessionId'],state=rel(STATE),status=s['status'],
  cpuThreads=2,gpu=0,singleJob=True,activeTask=s['activeTask'],exitCode=s['exitCode'],workerExpectedRunning=s['exitCode'] is None)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=s['status'],ownedJob=job,recordedAt=now(),encodedPixelExecution=rel(STATE),
  allFinalPixels=False,qa=False,collected=False,private=False,nextAction='Directly read every current final cue/cut/clause/PCM/spatial/member board; seal actual review, then QA/4files/private/Git.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(8):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);i=next(x for x in q['items']if x['slug']=='presenting-game-scores')
  i.update(stage=s['status'],currentExecution=job,currentJob=job,ownedJob=job,encodedPixelExecution=rel(STATE),allFinalPixels=False,qa=False,collected=False,uploaded=False,nextAction=cp['nextAction']);q['updatedAt']=now()
  if qp.read_text('utf-8-sig')==raw:save(qp,q);break
 else:raise RuntimeError('Concurrent queue preserved')
try:
 request['actualExtractionStarted']=True;save(request_path,request);s['requestSha256']=sha(request_path);checkpoint()
 expression="select='"+'+'.join(f'eq(pts,{f*1500})'for f in sorted(points))+"',showinfo";filter_path=DEST/'absolute-pts-select.filter';filter_path.write_text(expression,'utf-8')
 command=[str(FF),'-hide_banner','-v','info','-nostdin','-threads','2','-reinit_filter','0','-i',str(source),'-an',
  '-filter_threads','1','-filter_script:v',str(filter_path),'-fps_mode','passthrough','-frames:v',str(len(points)),'-threads','2',str(DEST/'frames/frame-%04d.png')]
 log=DEST/'extract.log'
 with log.open('w',encoding='utf-8')as stream:
  child=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  s['activeTask']=dict(pid=child.pid,createTime=psutil.Process(child.pid).create_time(),command=command,log=rel(log));checkpoint();code=child.wait()
 assert code==0,(code,rel(log))
 decoded=[int(x)for x in re.findall(r'\[Parsed_showinfo[^\]]*\]\s+n:\s*\d+\s+pts:\s*(\d+)',log.read_text('utf-8-sig'))]
 assert decoded==[f*1500 for f in sorted(points)],'Actual decoded PTS must match each selected frame.'
 files=sorted((DEST/'frames').glob('frame-*.png'));assert len(files)==len(points)
 for index,(path,frame,pts)in enumerate(zip(files,sorted(points),decoded),1):
  s['samples'].append(dict(index=index,**points[frame],decodedPts=pts,path=rel(path),sha256=sha(path),directlyRead=False))
 s.update(status='creating-current-final-review-boards',activeTask=None);checkpoint();font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
 for offset in range(0,len(files),6):
  rows=s['samples'][offset:offset+6];board=Image.new('RGB',(1920,1740),(18,18,18));draw=ImageDraw.Draw(board)
  for slot,row in enumerate(rows):
   x,y=slot%2*960,slot//2*580
   with Image.open(ROOT/row['path'])as im:assert im.size==(1920,1080);board.paste(im.resize((960,540)),(x,y+40))
   draw.text((x+5,y+4),f'{row["index"]:04d} f{row["frame"]} {row["segment"][:32]} cue{row["visibleCueIds"]}',font=font,fill='white')
  path=DEST/f'boards/board-{offset//6+1:03d}.jpg';board.save(path,quality=94,subsampling=0)
  s['boards'].append(dict(index=offset//6+1,path=rel(path),sha256=sha(path),sampleIndices=[r['index']for r in rows],directlyRead=False))
 s.update(status='closed-current-final-pixels-awaiting-full-direct-review',exitCode=0,endedAt=now(),activeTask=None,
  sampleCount=len(files),boardCount=len(s['boards']),allActualPtsMatched=True);checkpoint()
 print(json.dumps(dict(exitCode=0,frames=len(files),boards=len(s['boards']),allFinalPixels=False,newGitImages=0)),flush=True)
except BaseException:
 s.update(status='closed-current-final-pixel-extraction-failed',exitCode=1,endedAt=now(),activeTask=None,error=traceback.format_exc());checkpoint();raise
