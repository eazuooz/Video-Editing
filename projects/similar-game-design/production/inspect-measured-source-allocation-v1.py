"""Single CPU2 selected native crops/edges/onsets. No completed source decode or audio repeated."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,time,traceback,psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
PLAN=BASE/'measured-allocation-v1/plan.json';STATE=BASE/'measured-source-extraction-v1.json'
DEST=ROOT/'shared/output/similar-game-design/measured-source-qa-v1'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def now():return datetime.now(timezone.utc).isoformat()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
 for i in range(40):
  try:os.replace(t,p);return
  except OSError:
   if i==39:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
assert not STATE.exists() and not DEST.exists()
gate=subprocess.run(['node','scripts/review-video-duplicates.cjs','similar-game-design','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8');assert gate.returncode==0,gate.stdout+gate.stderr
plan=read(PLAN);assert plan['sceneCount']==24 and plan['paragraphCount']==73 and plan['candidateOnly'] and not plan['finalTimingApproved']
me=psutil.Process();state=dict(schemaVersion=1,startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),sessionId=None,status='single-CPU2-selected-native-crops-and-onsets',cpuThreads=2,gpuJobs=0,resource=resource,planPath=rel(PLAN),planSha256=sha(PLAN),sources=[],wholeSourceDecodeRepeated=False,previousBanksReextracted=False,localOnly=True,allBoardsDirectlyRead=False,exitCode=None)
DEST.mkdir(parents=True)
def checkpoint():
 sp=BASE/'measured-source-extraction-v1.session.json'
 if sp.exists():state['sessionId']=read(sp)['sessionId']
 state['updatedAt']=now();save(STATE,state)
 job=dict(status=state['status'],pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),sessionId=state['sessionId'],state=rel(STATE),cpuThreads=2,gpu=0,exitCode=state['exitCode'],workerExpectedRunning=state['exitCode'] is None)
 cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='current24-measured73-selected-source-native-review',currentSceneCount=24,currentParagraphCount=73,currentRawPcmSeconds=plan['rawPcmSeconds'],ownedJob=job,nextAction='Directly read every selected native crop/edge/onset board; retain input/final gates false. Then measured24 projected white motion/caption preparation, single white render, current mix and complete mixed ASR, pair and final pixel QA.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(8):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='similar-game-design');item.update(stage=cp['stage'],currentExecution=job,currentSceneCount=24,currentParagraphCount=73,currentRawPcmSeconds=plan['rawPcmSeconds'],nextAction=cp['nextAction'],currentDuplicateReview='production/batches/sakurai-planning-game-design/proof-similar-game-design/content-review-v13.json');q.update(updatedAt=now(),lastProgressAt=now())
  if qp.read_text('utf-8-sig')==raw:save(qp,q);break
  time.sleep(.15)
 else:raise RuntimeError('Concurrent queue write; foreign state preserved')
def run(cmd,log):
 with log.open('x',encoding='utf-8') as f:
  child=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT);state.update(childPid=child.pid,currentCommand=cmd);checkpoint();code=child.wait()
 assert code==0,f'{log} exit{code}';state['childPid']=None
try:
 checkpoint()
 for src in plan['sources']:
  cuts=[(i,p) for i,p in enumerate(plan['selectedNativeCuts']) if p['source']==src['id']]
  if not cuts:continue
  source=ROOT/src['path'];assert sha(source)==src['sha256'];targets={}
  def target(f,tag):targets.setdefault(f,[]).append(tag)
  for i,p in cuts:
   a,z=p['sourceInFrame'],p['sourceOutFrameExclusive']
   for f,label in [(a,'first'),(z-1,'last'),((a+z-1)//2,'middle')]:target(f,dict(cutIndex=i,scene=p['scene'],kind=label,finalFrame=p['startFrame']+f-a))
  for scene in plan['scenes']:
   for pi,para in enumerate(scene['paragraphs']):
    for f,label in [(para['localStartFrame']+15,'spoken-onset'),((para['localStartFrame']+para['localEndFrame'])//2,'paragraph-middle')]:
     p=next((p for p in scene['parts'] if p['role']=='actual' and p['localStartFrame']<=f<p['localEndFrameExclusive']),None)
     if p and p['source']==src['id']:target(p['sourceInFrame']+f-p['localStartFrame'],dict(scene=scene['id'],paragraph=pi+1,kind=label,finalFrame=scene['startFrame']+f,expectedKo=para['ko']))
  for sceneid,seconds,label in [('03-patterns-not-ranking',3.2,'named-long-light'),('03-patterns-not-ranking',4.4,'named-projectiles'),('03-patterns-not-ranking',6.2,'named-structures'),('10-playing-together',6.1,'named-multiple-avatars'),('18-target-and-effects',8.0,'named-large-green-target'),('06-follow-the-space',19.5,'named-gold-approach'),('24-destination-and-danger',6.5,'named-entered-circle')]:
   scene=next(s for s in plan['scenes'] if s['id']==sceneid);f=round(seconds*60);p=next((p for p in scene['parts'] if p['role']=='actual' and p['localStartFrame']<=f<p['localEndFrameExclusive']),None)
   if p and p['source']==src['id']:target(p['sourceInFrame']+f-p['localStartFrame'],dict(scene=sceneid,kind=label,finalFrame=scene['startFrame']+f))
  frames=sorted(targets);folder=DEST/src['id'];folder.mkdir()
  expr='+'.join(f'eq(n,{n})' for n in frames);crop=src['crop'];crop=crop if crop.startswith('crop=') else 'crop='+crop
  run([FF,'-hide_banner','-v','error','-threads','2','-i',str(source),'-an','-vf',f"select='{expr}',{crop},scale=640:360",'-vsync','0','-filter_threads','2','-threads','2','-q:v','2',str(folder/'frame-%04d.jpg')],folder/'extraction.log')
  images=sorted(folder.glob('frame-*.jpg'));assert len(images)==len(frames)
  entries=[dict(sourceFrame=f,sourceSeconds=f/60,path=rel(p),sha256=sha(p),targets=targets[f]) for f,p in zip(frames,images)]
  font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);boards=[]
  for offset in range(0,len(images),6):
   board=Image.new('RGB',(1920,796),'white');draw=ImageDraw.Draw(board)
   for j,img in enumerate(images[offset:offset+6]):
    index=offset+j;x=j%3*640;y=j//3*398;board.paste(Image.open(img),(x,y));tags=targets[frames[index]]
    draw.text((x+5,y+361),f"{src['id']} f{frames[index]} / {frames[index]/60:.4f}s",font=font,fill='black')
    draw.text((x+5,y+380),' | '.join(t['scene'][:2]+':'+t['kind'] for t in tags)[:80],font=font,fill='black')
   b=folder/f'board-{offset//6+1:02d}.jpg';board.save(b,quality=96);boards.append(dict(path=rel(b),sha256=sha(b),sourceFrames=frames[offset:offset+6],directlyRead=False))
  assert sha(source)==src['sha256'];state['sources'].append(dict(id=src['id'],sourcePath=src['path'],sourceSha256=src['sha256'],exactCrop=crop,frames=entries,boards=boards,allBoardsDirectlyRead=False));checkpoint()
  print(json.dumps(dict(source=src['id'],frames=len(frames),boards=len(boards))),flush=True)
 assert sha(PLAN)==state['planSha256'];state.update(status='closed-selected-native-extraction-awaiting-all-board-review',exitCode=0,finishedAt=now());checkpoint()
except BaseException:
 state.update(status='closed-selected-native-extraction-failed-preserving-files',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
