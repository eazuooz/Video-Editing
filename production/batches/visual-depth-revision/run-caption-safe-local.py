"""Serial CPU corrections, stopping at the encoded direct-pixel gate for every video."""
from pathlib import Path
import json,subprocess,datetime,os,sys,psutil
ROOT=Path(__file__).resolve().parents[3];BATCH=ROOT/'production/batches/visual-depth-revision'
PY='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
versions={'motion-sickness-games':'v3','hierarchical-game-outlines':'v4','game-reward-planning':'v3','avoid-game-comparisons':'v2','making-game-sequels':'v3','familiar-game-rules':'v4'}
slugs=sys.argv[1:]
if not slugs or len(set(slugs))!=len(slugs) or any(s not in versions for s in slugs):raise RuntimeError('Explicit authorized correction scope required')
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
statepath=BATCH/('caption-safe-pipeline-'+slugs[0]+'.json')
if statepath.exists():raise RuntimeError('Inspect prior pipeline; do not repeat')
state=dict(status='running',pid=os.getpid(),startedAt=now(),scope=slugs,completed=[],gpu=0,tts=0,serial=True,allFinalPixelsReviewed=False,uploaded=False)
def save():write(statepath,state)
def queue(slug,stage,pid=None):
 p=BATCH/'queue.json';q=read(p);item=next(i for i in q['items'] if i['slug']==slug)
 item.update(stage=stage,revision=versions[slug],pipelineExecution=statepath.relative_to(ROOT).as_posix(),pipelinePid=os.getpid(),activePid=pid,renderApproved=False,allPixelsReviewed=False)
 item.pop('pipelineSessionId',None);item.pop('sessionId',None)
 q.update(current=slug,updatedAt=now());write(p,q)
def observe():
 records=[]
 for p in psutil.process_iter(['pid','name','cmdline','create_time']):
  try:
   c=' '.join(p.info['cmdline'] or [])
   if p.info['name'] in ['python.exe','pythonw.exe','node.exe','ffmpeg.exe'] and any(s in c for s in ['visual-depth-revision','train_multiview.py','phase1_train_all_modes','gpu_queue.py','YamYamStudio']):records.append(p.info)
  except psutil.Error:pass
 gpu=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.used,memory.total','--format=csv,noheader'],capture_output=True,text=True,creationflags=0x08000000)
 state['resourceObservation']=dict(checkedAt=now(),processes=records,gpuObservation=gpu.stdout.strip(),foreignProcessesPreserved=True,gpuTtsHoldPreserved=True)
 save()
def run(slug,stage,args):
 observe();queue(slug,stage);log=ROOT/'projects'/slug/'production/visual-depth-v1'/('caption-safe-'+stage+'.log')
 if log.exists():raise RuntimeError('Preserve earlier stage log')
 state.update(slug=slug,stage=stage);save()
 with log.open('w',encoding='utf-8') as f:
  p=subprocess.Popen(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000);state.update(activePid=p.pid,activeCommand=args,log=log.relative_to(ROOT).as_posix());save();queue(slug,stage,p.pid);code=p.wait()
 state['completed'].append(dict(slug=slug,stage=stage,exitCode=code,endedAt=now(),log=log.relative_to(ROOT).as_posix()));state['activePid']=None;save()
 if code:raise RuntimeError(slug+' '+stage+' failed; preserve all evidence')
 print(slug+' '+stage+' exit0',flush=True)
try:
 save()
 for slug in slugs:
  revision=versions[slug];folder=ROOT/'projects'/slug/'production/visual-depth-v1'
  review=read(folder/'white-preflight-direct-review.json')
  if review.get('revision')!=revision or not review.get('preflightPixelsApproved') or not review.get('captionedPreflight'):raise RuntimeError('Current raw and captioned preflight direct reads required')
  run(slug,'white-render',['node',str(BATCH/'render-depth-cpu.cjs'),slug,revision])
  run(slug,'exact-white-input-review',[PY,str(BATCH/'prepare-rendered-assembly.py'),slug,revision])
  if slug=='motion-sickness-games':
   import hashlib
   sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
   fix=read(folder/'outro-boundary-fix.json');a=read(folder/'assembly-inputs.json');last=a['segments'][-1]
   if fix['frames']!=600 or fix['fullDecodeExitCode']!=0 or sha(ROOT/fix['path'])!=fix['sha256'] or last['originalSha256']!=fix['sourceSha256']:raise RuntimeError('Observed exact-source member fix required')
   last.update(file=fix['path'],sha256=fix['sha256'],boundaryFix='outro-boundary-fix.json');write(folder/'assembly-inputs.json',a)
  args=[PY,str(BATCH/'build-reviewed-pair.py'),slug]
  if slug in ['motion-sickness-games','hierarchical-game-outlines']:args.append('--resume-caption-safe')
  run(slug,'clean-captioned-pair',args)
  run(slug,'encoded-pixel-extraction',[PY,str(BATCH/'extract-final-pixels.py'),slug])
  queue(slug,'corrected-encoded-pixels-awaiting-direct-reading')
 state.update(status='corrected-encoded-pairs-awaiting-direct-reading',activePid=None,endedAt=now());save()
except Exception as e:
 state.update(status='failed',error=str(e),activePid=None,endedAt=now());save();raise
