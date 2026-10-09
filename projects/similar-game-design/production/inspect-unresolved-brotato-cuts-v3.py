"""Single CPU2/GPU0 lower-threshold detection for unresolved solo/co-op source cuts.
Previously reviewed five solo cut triples are preserved, not extracted again.
Detection candidates never constitute footage or pixel approval.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,subprocess,time,traceback,psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
STATE=BASE/'unresolved-brotato-cut-extraction-v3.json';DEST=ROOT/'shared/output/similar-game-design/preflight/unresolved-brotato-cuts-v3'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def now():return datetime.now(timezone.utc).isoformat()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
 for i in range(40):
  try:os.replace(t,p);return
  except OSError:
   if i==39:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args();resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
assert read(BASE/'fresh-guides-asr-execution-v4.json')['actualExitObserved']
assert not STATE.exists() and not DEST.exists();DEST.mkdir(parents=True)
me=psutil.Process();state=dict(schemaVersion=1,startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),
 sessionId=None,status='single-CPU2-new-unresolved-source-cuts',cpuThreads=2,gpuJobs=0,resource=resource,sources=[],
 wholeSourceDecodeRepeated=False,oldFiveSoloCutTriplesPreserved=True,localOnly=True,allBoardsDirectlyRead=False,exitCode=None)
def checkpoint():
 sp=BASE/'unresolved-brotato-cut-extraction-v3.session.json'
 if sp.exists():state['sessionId']=read(sp)['sessionId']
 state['updatedAt']=now();save(STATE,state)
 cp=read(BASE/'latest-checkpoint.json');job=dict(status=state['status'],pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),sessionId=state['sessionId'],
  state=rel(STATE),cpuThreads=2,gpu=0,exitCode=state['exitCode'],workerExpectedRunning=state['exitCode'] is None)
 cp.update(recordedAt=now(),stage='current24-new-native-montage-cut-coverage',ownedJob=job,
  nextAction='Directly read all newly detected solo/co-op source cut boards and distinguish hard cuts/dissolves from ordinary gameplay. Existing five solo triples/native banks are closed. Then exact73-paragraph measured allocation and60fps spatial/caption work.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(8):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='similar-game-design');item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction']);q.update(updatedAt=now(),lastProgressAt=now())
  if qp.read_text('utf-8-sig')==raw:save(qp,q);break
  time.sleep(.15)
 else:raise RuntimeError('Concurrent queue write; foreign state preserved')
def run(cmd,log):
 with log.open('x',encoding='utf-8') as f:
  p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT);state.update(childPid=p.pid,currentCommand=cmd);checkpoint();code=p.wait()
 assert code==0,f'{log} exit{code}';state['childPid']=None
sourceBank=read(ROOT/'shared/output/similar-game-design/preflight/primary-acquisition-v1.json')['sources']
try:
 checkpoint()
 for stem,start,end in [('brotato-full-release',120,3120),('brotato-local-coop',2400,3180)]:
  src=next(x for x in sourceBank if x['stem']==stem);source=ROOT/src['path'];assert sha(source)==src['sha256'];folder=DEST/stem;folder.mkdir()
  log=folder/'lower-threshold-cut-candidates.log'
  run([FF,'-hide_banner','-threads','2','-i',str(source),'-an','-vf',f"trim=start_frame={start}:end_frame={end},scale=320:180,select='gt(scene,0.08)',showinfo",'-filter_threads','2','-threads','2','-f','null','-'],log)
  cuts=sorted(set(round(float(t)*60) for t in re.findall(r'pts_time:([\d.]+)',log.read_text('utf-8')) if start<round(float(t)*60)<end))
  old=[550,880,1493,1748,2423] if stem=='brotato-full-release' else []
  new=[x for x in cuts if not any(abs(x-y)<=1 for y in old)]
  frames=sorted({n for c in new for n in [c-1,c,c+1] if start<=n<end}|({start,end-1} if stem=='brotato-local-coop' else set()))
  assert frames,'No unresolved candidates; inspect detection before proceeding.'
  expression='+'.join(f'eq(n,{x})' for x in frames)
  run([FF,'-hide_banner','-v','error','-threads','2','-i',str(source),'-an','-vf',f"select='{expression}',scale=640:360",'-vsync','0','-filter_threads','2','-threads','2','-q:v','2',str(folder/'frame-%04d.jpg')],folder/'extraction.log')
  images=sorted(folder.glob('frame-*.jpg'));assert len(images)==len(frames)
  entries=[dict(sourceFrame=f,sourceSeconds=f/60,path=rel(p),sha256=sha(p)) for f,p in zip(frames,images)]
  font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);boards=[]
  for offset in range(0,len(images),6):
   board=Image.new('RGB',(1920,776),'white');draw=ImageDraw.Draw(board)
   for j,img in enumerate(images[offset:offset+6]):
    x=j%3*640;y=j//3*388;board.paste(Image.open(img),(x,y));draw.text((x+5,y+363),f'{stem} source f{frames[offset+j]} / {frames[offset+j]/60:.6f}s',font=font,fill='black')
   p=folder/f'board-{offset//6+1:02d}.jpg';board.save(p,quality=96);boards.append(dict(path=rel(p),sha256=sha(p),frames=frames[offset:offset+6],directlyRead=False))
  assert sha(source)==src['sha256'];state['sources'].append(dict(stem=stem,sourcePath=src['path'],sourceSha256=src['sha256'],
   allDetectedCandidates=cuts,newCandidates=new,oldCutTriplesNotReextracted=old,frameEntries=entries,boards=boards,allBoardsDirectlyRead=False));checkpoint()
  print(json.dumps(dict(stem=stem,newCandidates=new,frames=len(frames),boards=len(boards))),flush=True)
 state.update(status='closed-unresolved-source-cut-extraction-awaiting-direct-review',exitCode=0,finishedAt=now());checkpoint()
except BaseException:
 state.update(status='closed-source-cut-extraction-failed-preserving-files',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
