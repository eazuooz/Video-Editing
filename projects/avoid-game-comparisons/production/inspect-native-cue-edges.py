"""Local-only new cut edges and the held launch trailer's short gameplay section."""
from pathlib import Path
from datetime import datetime,timezone
from collections import defaultdict
import hashlib,json,os,subprocess,traceback,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons'
RAW=PROOF/'research-local/game-sources';OUT=PROOF/'research-local/native-cue-new-edges'
STATE=BASE/'native-cue-edges-execution.json';FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def rel(p):return p.relative_to(ROOT).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');t.replace(p)
historical=[]
if STATE.exists() and '--recover-initial-checkpoint' in sys.argv:
 previous=read(STATE);assert previous['status']=='initializing' and not previous['sources'] and previous['childPid'] is None
 previous.update(status='failed-before-any-source-extraction',cpuJobs=0,exitCode=1,endedAt=now(),error='Initial queue checkpoint used a function instead of its timestamp value; no ffmpeg child or source extraction started.')
 preserved=BASE/f"native-cue-edges-initial-checkpoint-failure-{previous['pid']}.json";assert not preserved.exists();save(preserved,previous)
 historical=previous.get('historicalExecutionFailures',[])+[dict(state=rel(preserved),pid=previous['pid'],sourceExtractionStarted=False,reason=previous['error'])]
elif STATE.exists():raise RuntimeError('Reuse current extraction evidence; never repeat a closed worker.')
proposal=read(BASE/'native-cue-proposal.json');bank=read(PROOF/'source-research/source-action-bank-v4.json');old={x['id']:x for x in bank['clips']}
points=defaultdict(set);rates={}
for g in proposal['groups']:
 for c in g['sourceCuts']:
  sid=c['sourceVideoId'];rates[sid]=c['nativeFps'];base=old[c['id']]
  if c['startFrame']!=base['startFrame']:points[sid].update([c['startFrame']-1,c['startFrame'],c['startFrame']+1])
  if c['endFrameExclusive']!=base['endFrameExclusive']:points[sid].update([c['endFrameExclusive']-2,c['endFrameExclusive']-1,c['endFrameExclusive'],c['endFrameExclusive']+1])
# New research only: physical advertisement remains excluded. Inspect transition/short gameplay/title edges.
points['xREgLxEzZE4'].update(range(2592,2797,3));rates['xREgLxEzZE4']=30
state=dict(schemaVersion=1,pid=os.getpid(),sessionId=None,startedAt=now(),status='initializing',cpuJobs=1,gpuJobs=0,renderJobs=0,uploads=0,sources=[],childPid=None,localOnlyImages=True,newGitImages=0,sourceAudioUsed=False,exactBoundaryApproval=False,bodyRatioApproved=False,historicalExecutionFailures=historical)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
def checkpoint():
 launch=BASE/'native-cue-edges-session.json'
 if launch.exists():
  x=read(launch)
  if x['pid']==os.getpid():state['sessionId']=x['sessionId']
 state['updatedAt']=now();save(STATE,state)
 qpath=PROOF.parent/'queue.json';q=read(qpath);task=next(x for x in q['items'] if x['slug']=='avoid-game-comparisons')
 task.update(stage='current15-native-cue-exact-boundary-and-held-launch-review',updatedAt=now(),nextAction='Read each new exact native edge and held launch gameplay sample; compare with existing clips before assigning unique seconds. Current15 PCM are preserved; final ratio, fixed captions, mix/render and delivery are pending.')
 task['execution'].update(observedAt=now(),phase='single-CPU-new-native-cue-edge-inspection',status=state['status'],pid=os.getpid(),sessionId=state['sessionId'],childPid=state['childPid'],alive=bool(state['cpuJobs']),gpuSynthesisJobs=0,cpuProductionJobs=state['cpuJobs'],primaryCpuProductionJobs=state['cpuJobs'],renderJobs=0,uploads=0,state=rel(STATE),activeTasks=[] if not state['cpuJobs'] else [dict(kind='new-native-cut-edges',pid=os.getpid(),sessionId=state['sessionId'],childPid=state['childPid'])]);task['nativeCueEdgeReview']=dict(state=rel(STATE),status=state['status'],directPixelReview=False)
 q.update(updatedAt=now(),lastProgressAt=now());save(qpath,q)
 for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
  d=read(p)
  for k in ['stage','updatedAt','execution','nextAction','nativeCueEdgeReview']:d[k]=task[k]
  save(p,d)
checkpoint()
try:
 for sid,ns in points.items():
  frames=sorted(ns);folder=OUT/sid;folder.mkdir(parents=True,exist_ok=True);source=RAW/(sid+'.mp4')
  record=dict(videoId=sid,source=rel(source),sourceSha256=sha(source),nativeFps=rates[sid],selectedNativeFrameNumbers=frames,frames=[],sheets=[],directReview=False)
  state['sources'].append(record);state.update(status='extracting-'+sid);checkpoint()
  expression='+'.join(f'eq(n\\,{n})' for n in frames);log=folder/'extract.log'
  with log.open('wb') as f:
   child=subprocess.Popen([FF,'-hide_banner','-threads','2','-filter_threads','1','-i',str(source),'-an','-vf',f'select={expression},scale=960:540','-fps_mode','vfr','-frames:v',str(len(frames)),str(folder/'frame-%04d.jpg')],stdout=f,stderr=f,creationflags=subprocess.CREATE_NO_WINDOW)
   state['childPid']=child.pid;record['log']=rel(log);checkpoint();code=child.wait();state['childPid']=None;assert code==0,(sid,code)
  images=sorted(folder.glob('frame-*.jpg'));assert len(images)==len(frames),(sid,len(images),len(frames))
  for n,p in zip(frames,images):record['frames'].append(dict(frame=n,seconds=n/rates[sid],path=rel(p),sha256=sha(p)))
  for offset in range(0,len(images),16):
   sheet=Image.new('RGB',(2560,1552),'#eeeeee');draw=ImageDraw.Draw(sheet)
   for j,(p,n) in enumerate(zip(images[offset:offset+16],frames[offset:offset+16])):
    im=Image.open(p).resize((640,360));x=(j%4)*640;y=(j//4)*388;sheet.paste(im,(x,y+28));draw.text((x+4,y+2),f'{sid} n{n} {n/rates[sid]:.5f}s',font=font,fill='black')
   p=folder/f'edge-sheet-{offset//16+1:02d}.jpg';sheet.save(p,quality=94);record['sheets'].append(dict(path=rel(p),sha256=sha(p),tiles=min(16,len(images)-offset)))
  record['status']='extracted-awaiting-direct-pixels';checkpoint()
 state.update(status='new-native-edge-extraction-complete-awaiting-direct-pixels',cpuJobs=0,exitCode=0,endedAt=now(),childPid=None);checkpoint()
 print(json.dumps(dict(pid=state['pid'],sources=len(state['sources']),nativeFrames=sum(len(x['frames']) for x in state['sources']),sheets=sum(len(x['sheets']) for x in state['sources']),actualCutApproved=False,newGitImages=0)))
except BaseException:
 state.update(status='failed',cpuJobs=0,exitCode=1,error=traceback.format_exc(),endedAt=now());checkpoint();raise
