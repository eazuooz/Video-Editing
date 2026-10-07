"""Wait for the observed owned CPU pipeline, then generate only two current preflights."""
from pathlib import Path
import json,subprocess,datetime,os,time,psutil
ROOT=Path(__file__).resolve().parents[3];BATCH=ROOT/'production/batches/visual-depth-revision'
PY='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
statepath=BATCH/'refined-v4-preflight-execution.json'
if statepath.exists():raise RuntimeError('Inspect actual prior preflight execution; do not repeat')
state=dict(status='waiting-for-observed-owned-pipeline',pid=os.getpid(),startedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),waitingOwner=dict(pid=15792,createTime=1791340652.5792072,script='production/batches/visual-depth-revision/run-caption-safe-local.py',slug='motion-sickness-games'),completed=[],gpu=0,tts=0,allFinalPixelsReviewed=False)
def save():statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
try:
 save()
 while True:
  old=read(BATCH/'caption-safe-pipeline-motion-sickness-games.json')
  if old['status']=='failed':raise RuntimeError('Observed pipeline failed; inspect it first')
  try:
   p=psutil.Process(15792)
   if abs(p.create_time()-1791340652.5792072)>.01 or p.cmdline()[1:]!=['production/batches/visual-depth-revision/run-caption-safe-local.py','motion-sickness-games']:raise RuntimeError('PID identity changed; do not infer completion')
   time.sleep(1);continue
  except psutil.NoSuchProcess:
   if old['status']!='corrected-encoded-pairs-awaiting-direct-reading':raise RuntimeError('Previous job disappeared before completed checkpoint')
   break
 state.update(status='preparing-current-authored-samples',previousPipelineEndedAt=old['endedAt']);save()
 for slug in ['hierarchical-game-outlines','familiar-game-rules']:
  folder=ROOT/'projects'/slug/'production/visual-depth-v1'
  for stage,args in [('raw',['node',str(BATCH/'render-depth-cpu.cjs'),slug,'v4','--lookdev-only']),('boards',[PY,str(BATCH/'prepare-white-boards.py'),slug,'v4','--preflight']),('actual-ass',[PY,str(BATCH/'prepare-caption-preflight.py'),slug,'v4'])]:
   log=folder/('v4-preflight-'+stage+'.log')
   if log.exists():raise RuntimeError('Preserve previous v4 preflight log')
   with log.open('w',encoding='utf-8') as f:
    p=subprocess.Popen(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000);state.update(slug=slug,stage=stage,activePid=p.pid,command=args,log=log.relative_to(ROOT).as_posix());save();code=p.wait()
   state['completed'].append(dict(slug=slug,stage=stage,exitCode=code,endedAt=now()));state['activePid']=None;save()
   if code:raise RuntimeError('Actual v4 preflight failed; preserve log')
 state.update(status='current-raw-and-ass-preflights-awaiting-direct-reading',endedAt=now());save()
except Exception as e:
 state.update(status='failed',error=str(e),endedAt=now());save();raise
