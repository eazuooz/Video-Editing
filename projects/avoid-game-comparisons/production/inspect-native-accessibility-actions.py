"""Inspect only newly proposed regions from an already acquired official source."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,traceback
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons'
STATE=BASE/'native-accessibility-actions-execution.json'
OUT=PROOF/'research-local/native-accessibility-actions/JdNZo7E_hXU'
SOURCE=PROOF/'research-local/game-sources/JdNZo7E_hXU.mp4'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');t.replace(p)
def rel(p):return p.relative_to(ROOT).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not STATE.exists(),'Inspect the saved result; never repeat a closed worker.'
index=read(BASE/'narration-expanded15-index.json')
for m in index['measurements']:assert sha(ROOT/m['path'])==m['sha256'],m['scene']
frames=sorted(set(range(3718,3970,6))|set(range(4170,4362,6))|{3717,3719,3720,3721,3958,3959,3960,3961,4168,4169,4170,4171,4358,4359,4360,4361,4020,4080,4140})
state=dict(schemaVersion=1,pid=os.getpid(),sessionId=None,startedAt=now(),status='initializing',cpuJobs=1,gpuJobs=0,renderJobs=0,uploads=0,childPid=None,source=rel(SOURCE),sourceSha256=sha(SOURCE),nativeFps=60,selectedFrames=frames,frames=[],sheets=[],localOnlyImages=True,newGitImages=0,sourceAudioUsed=False,uniqueSecondsApproved=False,bodyRatioApproved=False)
assert state['sourceSha256']=='a867ae3337e9e1a0a3913e685b034a6f9ad758bbfa72c64db46cfc7ab3cbacad'
def checkpoint():
 launch=BASE/'native-accessibility-actions-session.json'
 if launch.exists():
  s=read(launch)
  if s['pid']==os.getpid():state['sessionId']=s['sessionId']
 state['updatedAt']=now();save(STATE,state)
 qpath=PROOF.parent/'queue.json';q=read(qpath);task=next(i for i in q['items'] if i['slug']=='avoid-game-comparisons')
 task.update(stage='current15-additional-official-accessibility-action-review',updatedAt=now(),nextAction='Read new normal-speed bright-page and option-context desk combat native samples; directly compare all related existing shots before adopting unique seconds. Preserve all15 PCM and final approval=false.')
 task['execution'].update(observedAt=now(),phase='single-CPU-new-accessibility-action-inspection',status=state['status'],pid=os.getpid(),sessionId=state['sessionId'],childPid=state['childPid'],alive=bool(state['cpuJobs']),gpuSynthesisJobs=0,cpuProductionJobs=state['cpuJobs'],primaryCpuProductionJobs=state['cpuJobs'],renderJobs=0,uploads=0,state=rel(STATE),activeTasks=[] if not state['cpuJobs'] else [dict(kind='new-accessibility-actions',pid=os.getpid(),sessionId=state['sessionId'])])
 task['nativeAccessibilityActionReview']=dict(state=rel(STATE),directPixelReview=False,uniqueSecondsApproved=False)
 q.update(updatedAt=now(),lastProgressAt=now());save(qpath,q)
 for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
  d=read(p)
  for k in ['stage','updatedAt','execution','nextAction','nativeAccessibilityActionReview']:d[k]=task[k]
  save(p,d)
checkpoint()
try:
 OUT.mkdir(parents=True,exist_ok=True);log=OUT/'extract.log'
 expression='+'.join(f'eq(n\\,{n})' for n in frames)
 with log.open('wb') as f:
  child=subprocess.Popen([FF,'-hide_banner','-threads','2','-filter_threads','1','-i',str(SOURCE),'-an','-vf',f'select={expression},scale=960:540','-fps_mode','vfr','-frames:v',str(len(frames)),str(OUT/'frame-%04d.jpg')],stdout=f,stderr=f,creationflags=subprocess.CREATE_NO_WINDOW)
  state.update(status='extracting-new-candidate-edges-and-option-context',childPid=child.pid,log=rel(log));checkpoint();code=child.wait();state['childPid']=None;assert code==0,code
 images=sorted(OUT.glob('frame-*.jpg'));assert len(images)==len(frames)
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
 for n,p in zip(frames,images):state['frames'].append(dict(frame=n,seconds=n/60,path=rel(p),sha256=sha(p)))
 for offset in range(0,len(images),16):
  sheet=Image.new('RGB',(2560,1552),'#eeeeee');draw=ImageDraw.Draw(sheet)
  for j,(n,p) in enumerate(zip(frames[offset:offset+16],images[offset:offset+16])):
   x=(j%4)*640;y=(j//4)*388;sheet.paste(Image.open(p).resize((640,360)),(x,y+28));draw.text((x+4,y+2),f'JdNZo7E_hXU n{n} {n/60:.5f}s',font=font,fill='black')
  p=OUT/f'sheet-{offset//16+1:02d}.jpg';sheet.save(p,quality=94);state['sheets'].append(dict(path=rel(p),sha256=sha(p),tiles=min(16,len(images)-offset)))
 state.update(status='closed-new-native-actions-awaiting-direct-duplicate-context-review',cpuJobs=0,exitCode=0,endedAt=now());checkpoint()
 print(json.dumps({'pid':state['pid'],'frames':len(images),'sheets':len(state['sheets']),'uniqueSecondsApproved':False,'newGitImages':0}))
except BaseException:
 state.update(status='failed',cpuJobs=0,exitCode=1,error=traceback.format_exc(),endedAt=now());checkpoint();raise
