"""One CPU worker: proposed natural-rate native frames + literal caption trials.

All images remain local. These source inputs are not final encoded pixels.
"""
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction
import argparse,hashlib,json,math,os,subprocess,sys,time,traceback
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
parser=argparse.ArgumentParser();parser.add_argument('--plan-only',action='store_true');parser.add_argument('--resource');args=parser.parse_args()
plan_path=BASE/'word-action-source-candidate-v1.json';plan=read(plan_path)
assert not plan['finalTimelineAdopted'] and not plan['allFinalCaptionPixelsReviewed']
cuts=[c for p in plan['pieces'] for c in p['selectedSourceCuts']]
frames={}
def add(n,tag):
 c=next((c for c in cuts if c['startFrame']<=n<c['endFrame']),None)
 if c:frames.setdefault(n,set()).add(tag)
game_cues=[]
for cue in plan['ko']:
 a=math.ceil(cue['startSeconds']*60);z=math.ceil(cue['endSeconds']*60)-1
 if not any(c['startFrame']<=a<c['endFrame'] for c in cuts):continue
 game_cues.append(cue['index'])
 for n,tag in [(a,'cue-first'),((a+z)//2,'cue-middle'),(z,'cue-last')]:add(n,f'{tag}:{cue["index"]}')
 for c in cuts:
  if a<c['startFrame']<=z:
   for n in [c['startFrame']-1,c['startFrame']]:add(n,f'cut-inside-cue:{cue["index"]}')
for c in cuts:
 for n,tag in [(c['startFrame'],'cut-first'),(c['startFrame']+1,'cut-after-first'),
  ((c['startFrame']+c['endFrame']-1)//2,'cut-middle'),(c['endFrame']-2,'cut-before-last'),(c['endFrame']-1,'cut-last')]:add(n,tag)
 step=15 if c['logicalScene'] in ['12','15','16','17','18','19'] or c['pieceId']=='10-part1' else 30
 for n in range(c['startFrame'],c['endFrame'],step):add(n,'motion-quarter-second' if step==15 else 'motion-half-second')
samples=[];native={}
for n,tags in sorted(frames.items()):
 c=next(c for c in cuts if c['startFrame']<=n<c['endFrame']);fps=Fraction(c['sourceFrameRate'])
 sf=min(c['outFrameExclusive']-1,c['inFrameInclusive']+math.floor(Fraction(n-c['startFrame'],60)*fps))
 cue=next((q for q in plan['ko'] if q['startSeconds']<=n/60<q['endSeconds']),None)
 samples.append(dict(outputFrame=n,pieceId=c['pieceId'],scene=c['logicalScene'],cutId=c['id'],sourceVideoId=c['sourceVideoId'],
  sourceFrame=sf,captionIndex=cue['index'] if cue else None,literalKo=cue['ko'] if cue else None,tags=sorted(tags),directlyRead=False))
 native.setdefault(c['sourceVideoId'],set()).add(sf)
trial_plan=dict(schemaVersion=1,slug='familiar-game-rules',preparedAt=now(),candidate=rel(plan_path),candidateSha256=sha(plan_path),
 samples=samples,sampleCount=len(samples),uniqueNativeFrames=sum(len(s) for s in native.values()),allActualCutCount=len(cuts),
 actualKoCueCount=len(game_cues),actualKoCueIndices=game_cues,whiteKoCueCount=len(plan['ko'])-len(game_cues),
 completeOriginalWhiteAndGuideDiagramsPending=True,captionCenter=[960,970],fontPx=48,sourceCrop=[0,0,1920,1080],
 imagesGitPolicy='local-only',newGitImages=0,allDirectlyRead=False,finalPixelsReviewed=False,
 scope='Every proposed game cue/cut plus0.25/0.5second native-motion anchors; exact source and PIL caption-composition candidates. Final ASS/MC/burned encoded pixels remain separate.')
trial_plan_path=PROOF/'word-cue-input-trial-plan-v1.json'
if args.plan_only:
 assert not trial_plan_path.exists();save(trial_plan_path,trial_plan)
 print(json.dumps({k:trial_plan[k] for k in ['sampleCount','uniqueNativeFrames','actualKoCueCount','whiteKoCueCount','allActualCutCount']}));sys.exit()
assert args.resource and trial_plan_path.exists()
stored=read(trial_plan_path);assert stored['candidateSha256']==sha(plan_path) and stored['samples']==trial_plan['samples']
r=read(ROOT/args.resource);assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'].replace('Z','+00:00'))).total_seconds()<240
STATE=PROOF/'word-cue-input-trial-execution-v1.json';LOG=BASE/'word-cue-input-trial-v1.log'
out=ROOT/'shared/output/familiar-game-rules/research/word-cue-input-trials-v1'
assert not STATE.exists() and not out.exists();out.mkdir(parents=True);(out/'boards').mkdir();(out/'captioned').mkdir()
state=dict(schemaVersion=1,slug='familiar-game-rules',pid=os.getpid(),sessionId=None,commandLine=[sys.executable,*sys.argv],startedAt=now(),
 status='extracting-proposed-word-cue-native-inputs',cpuThreads=2,gpuJobs=0,resourceObservation=r,
 plan=rel(trial_plan_path),planSha256=sha(trial_plan_path),log=rel(LOG),tasks=[],activeTasks=[],
 sourceCount=len(native),completedSources=0,imagesGitPolicy='local-only',newGitImages=0,exitCode=None,
 allDirectlyRead=False,allFinalCaptionPixelsReviewed=False,renderedFinal=False)
def checkpoint():
 sp=STATE.with_name(STATE.stem+'.session.json')
 if sp.exists():
  s=read(sp)
  if s['pid']==os.getpid():state['sessionId']=s['sessionId']
 state['updatedAt']=now();save(STATE,state)
 qp=PROOF.parent/'queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
 if item.get('execution',{}).get('pid')!=os.getpid():item.setdefault('executionHistory',[]).append(item.get('execution',{}))
 running=state['exitCode'] is None
 item.update(stage='current70-paragraph78cuts-literal-game-input-CPU-QA',updatedAt=now(),
  measuredTimingCandidate='projects/familiar-game-rules/production/measured-word-timing-candidate-v2.json',
  wordCaptionCandidate='projects/familiar-game-rules/production/word-caption-candidate-v2/captions.json',
  wordActionSourceCandidate=rel(plan_path),guide12RoomContextsDirectReview='projects/familiar-game-rules/production/guide12-room-contexts-direct-review-v2.json',
  inputWordCueTrialPlan=rel(trial_plan_path),inputWordCueTrialExecution=rel(STATE),
  execution=dict(pid=os.getpid(),commandLine=state['commandLine'],sessionId=state['sessionId'],alive=running,status=state['status'],
   state=rel(STATE),log=rel(LOG),cpuThreads=2,gpuJobs=0,completed=state['completedSources'],total=state['sourceCount'],activeTasks=state['activeTasks']),
  nextAction='Observe the one CPU native/literal input QA worker. After actual exit, directly read all current cue/cut/motion boards, fix focus/overlap/edge issues, then independent white6+2 and measured timing adoption. Original11/current8PCM373.680083333s preserved; candidate23570frames only. Final mix/ASR/clean-captioned render/encodedQA/collection/private false.')
 q.update(updatedAt=now(),lastProgressAt=now());save(qp,q)
 for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
  d=read(p)
  for k in ['stage','updatedAt','execution','measuredTimingCandidate','wordCaptionCandidate','wordActionSourceCandidate','guide12RoomContextsDirectReview','inputWordCueTrialPlan','inputWordCueTrialExecution','nextAction']:d[k]=item[k]
  d.update(asrApproved=False,narrationApproved=False,finalRatioApproved=False);save(p,d)
original=sys.stdout
class Tee:
 def __init__(self,f):self.f=f
 def write(self,s):original.write(s);original.flush();self.f.write(s);self.f.flush();return len(s)
 def flush(self):original.flush();self.f.flush()
with LOG.open('x',encoding='utf-8') as log:
 sys.stdout=Tee(log);sys.stderr=sys.stdout
 try:
  checkpoint();frame_paths={}
  for vid,indices in native.items():
   c=next(c for c in cuts if c['sourceVideoId']==vid);src=ROOT/c['sourcePath'];assert sha(src)==c['sourceSha256']
   dest=out/'native'/vid;dest.mkdir(parents=True)
   selected=sorted(indices);expression='+'.join(f'eq(n,{i})' for i in selected)
   cmd=[FF,'-hide_banner','-v','error','-nostdin','-threads','2','-filter_threads','1','-i',str(src),'-an',
    '-vf',f"select='{expression}',scale=1920:1080",'-vsync','0','-q:v','3','-threads','2',str(dest/'%05d.jpg')]
   process=subprocess.Popen(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
   task=dict(sourceVideoId=vid,pid=process.pid,commandLine=cmd,startedAt=now(),expectedFrames=len(selected),status='running')
   state['tasks'].append(task);state['activeTasks']=[dict(pid=process.pid,sourceVideoId=vid)];checkpoint()
   output,_=process.communicate();print(output,flush=True) if output else None
   task.update(exitCode=process.returncode,status='finished' if process.returncode==0 else 'failed',endedAt=now())
   assert process.returncode==0,vid
   files=sorted(dest.glob('*.jpg'));assert len(files)==len(selected),(vid,len(files),len(selected))
   for n,p in zip(selected,files):frame_paths[(vid,n)]=dict(path=rel(p),sha256=sha(p))
   state['completedSources']+=1;state['activeTasks']=[];checkpoint();print(json.dumps(dict(source=vid,frames=len(files))),flush=True)
  font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48);label=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
  for i,s in enumerate(samples,1):
   raw=frame_paths[(s['sourceVideoId'],s['sourceFrame'])];s.update(nativePath=raw['path'],nativeSha256=raw['sha256'])
   with Image.open(ROOT/raw['path']) as im:im=im.convert('RGB')
   assert im.size==(1920,1080)
   if s['literalKo']:
    width=round(font.getlength(s['literalKo'])+44);height=84;left=960-width/2;top=970-height/2
    draw=ImageDraw.Draw(im);draw.rectangle((left+14,top+14,left+width+14,top+height+14),fill='#073c32')
    draw.rectangle((left,top,left+width,top+height),fill='white',outline='#161b18',width=3)
    draw.text((960,top+11),s['literalKo'],font=font,fill='#080b09',anchor='mt');s['captionBox']=[left,top,width,height]
   p=out/'captioned'/f'{i:05}.jpg';im.save(p,quality=95);s.update(index=i,path=rel(p),sha256=sha(p))
  boards=[]
  for start in range(0,len(samples),6):
   im=Image.new('RGB',(1920,1710),'white');draw=ImageDraw.Draw(im)
   rows=samples[start:start+6]
   for i,s in enumerate(rows):
    x=i%2*960;y=i//2*570
    draw.text((x+6,y+1),f'{s["index"]} f{s["outputFrame"]} {s["pieceId"]} cue{s["captionIndex"]} {s["sourceVideoId"]}@{s["sourceFrame"]}',font=label,fill='black')
    with Image.open(ROOT/s['path']) as tile:im.paste(tile.resize((960,540)),(x,y+30))
   p=out/'boards'/f'{start//6+1:03}.jpg';im.save(p,quality=95)
   boards.append(dict(index=start//6+1,path=rel(p),sha256=sha(p),sampleIndices=[s['index'] for s in rows],directlyRead=False))
  evidence={**stored,'createdAt':now(),'samples':samples,'boards':boards,'boardCount':len(boards),
   'allRawSourceShasMatched':True,'literalCaptionTrialOnly':True,'allDirectlyRead':False,'finalPixelsReviewed':False,
   'actualExtractedNativeFrames':len(frame_paths),'actualCaptionTrialImages':len(samples),'newGitImages':0}
  evidence_path=PROOF/'word-cue-input-trials-v1.json';assert not evidence_path.exists();save(evidence_path,evidence)
  state.update(status='closed-input-native-literal-trials-awaiting-all-board-direct-review',activeTasks=[],exitCode=0,endedAt=now(),
   evidence=rel(evidence_path),evidenceSha256=sha(evidence_path),actualExtractedNativeFrames=len(frame_paths),
   actualCaptionTrialImages=len(samples),boardCount=len(boards));checkpoint()
  print(json.dumps(dict(native=len(frame_paths),captioned=len(samples),boards=len(boards),approved=False)),flush=True)
 except BaseException:
  state.update(status='failed-input-native-literal-trials',exitCode=1,endedAt=now(),error=traceback.format_exc());checkpoint();traceback.print_exc();raise
 finally:sys.stdout=original;sys.stderr=original
