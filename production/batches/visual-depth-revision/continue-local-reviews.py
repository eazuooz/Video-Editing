"""Serial CPU-only preparation of the six authorized corrections; stop at final direct-pixel gates.
No TTS, browser, upload, Git write or new topic. The first existing motion render is reused.
"""
from pathlib import Path
import json,subprocess,datetime,time,os,psutil
ROOT=Path(__file__).resolve().parents[3];BATCH=ROOT/'production/batches/visual-depth-revision'
PY='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
slugs=['motion-sickness-games','hierarchical-game-outlines','game-reward-planning','avoid-game-comparisons','making-game-sequels','familiar-game-rules']
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
statepath=BATCH/'local-review-pipeline-execution.json'
if statepath.exists():raise RuntimeError('Inspect existing pipeline; do not repeat')
state=dict(status='running',pid=os.getpid(),startedAt=now(),gpu=0,tts=0,serial=True,scope=slugs,completed=[],allFinalPixelsReviewed=False,uploaded=False);write(statepath,state)
def save():write(statepath,state)
def queue(slug,stage):
 p=BATCH/'queue.json';q=read(p);item=next(i for i in q['items'] if i['slug']==slug);item.update(stage=stage,pipelineExecution=statepath.relative_to(ROOT).as_posix(),pipelinePid=os.getpid());q['updatedAt']=now();write(p,q)
def observe():
 records=[]
 for p in psutil.process_iter(['pid','name','cmdline']):
  try:
   c=' '.join(p.info['cmdline'] or [])
   if p.info['name'] in ['python.exe','pythonw.exe','node.exe','ffmpeg.exe'] and any(s in c for s in ['visual-depth-revision','train_multiview.py','phase1_train_all_modes','gpu_queue.py','YamYamStudio']):records.append(p.info)
  except psutil.Error:pass
 state['resourceObservation']=dict(checkedAt=now(),processes=records,foreignProcessesPreserved=True,gpuTtsHoldPreserved=True);save()
def run(slug,stage,args):
 observe();queue(slug,stage);log=ROOT/'projects'/slug/'production/visual-depth-v1'/('pipeline-'+stage+'.log')
 state.update(slug=slug,stage=stage);save()
 with log.open('w',encoding='utf-8') as f:
  p=subprocess.Popen(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000);state.update(activePid=p.pid,activeCommand=args,log=log.relative_to(ROOT).as_posix());save();code=p.wait()
 state['completed'].append(dict(slug=slug,stage=stage,exitCode=code,endedAt=now(),log=log.relative_to(ROOT).as_posix()));state['activePid']=None;save()
 if code:raise RuntimeError(slug+' '+stage+' failed; preserve state/log/output')
 print(slug+' '+stage+' exit0',flush=True)
try:
 first=ROOT/'projects'/slugs[0]/'production/visual-depth-v1/white-cpu-execution.json'
 state.update(slug=slugs[0],stage='reuse-existing-white-render');save()
 while True:
  e=read(first)
  if e['status']=='rendered-pending-direct-pixels-and-full-decode':break
  if e['status']!='running':raise RuntimeError('Existing first white render must be inspected')
  try:
   p=psutil.Process(e['pid']);cmd=p.cmdline()
   if not any(a.endswith('render-depth-cpu.cjs') for a in cmd) or slugs[0] not in cmd:raise RuntimeError('Existing white PID command changed')
  except psutil.NoSuchProcess:raise RuntimeError('Existing render no longer alive without completion evidence')
  state.update(activePid=e['pid'],activeCommand=cmd);save();time.sleep(2)
 for i,slug in enumerate(slugs):
  if i:run(slug,'white-render',['node',str(BATCH/'render-depth-cpu.cjs'),slug,'v1'])
  run(slug,'exact-white-input-review',[PY,str(BATCH/'prepare-rendered-assembly.py'),slug])
  run(slug,'clean-captioned-pair',[PY,str(BATCH/'build-reviewed-pair.py'),slug])
  run(slug,'encoded-pixel-extraction',[PY,str(BATCH/'extract-final-pixels.py'),slug])
  queue(slug,'encoded-pixels-awaiting-direct-reading-no-upload');print(slug+' final direct pixel review pending',flush=True)
 state.update(status='six-encoded-pairs-awaiting-direct-pixel-reading',endedAt=now(),activePid=None);save()
except Exception as e:
 state.update(status='failed',error=str(e),endedAt=now());save();raise
