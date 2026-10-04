"""Render only the source-specific clothing/mask paragraph candidate."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'repair2'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();now=lambda:datetime.now(timezone.utc).isoformat()
request=read(WORK/'request.json');STATE=WORK/'tts-execution.json';QUEUE=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
assert not STATE.exists(),'Preserve existing candidate.'
for lock in request['inputLocks']:assert sha(ROOT/lock['path'])==lock['sha256']
for sid,h in request['originalWavLocks'].items():assert sha(ROOT/request['originalWavDirectory']/(sid+'-scene.wav'))==h
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','game-reward-planning','--check'],cwd=ROOT,check=True)
state={'pid':os.getpid(),'startedAt':now(),'status':'waiting-for-free-gpu','gpuJobs':0,'scope':['08b'],'original13WavsPreserved':True,'autoSplice':False,'humanListening':'pending','log':'projects/game-reward-planning/production/repair2/tts.log','gpuObservations':[]}
def write(p,v):
 temp=p.with_suffix(p.suffix+'.'+str(os.getpid())+'.writing')
 for attempt in range(13):
  try:temp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');temp.replace(p);return
  except OSError:
   if attempt==12:raise
   time.sleep(.1)
def save():
 state['updatedAt']=now();write(STATE,state);q=read(QUEUE);i=next(x for x in q['items'] if x['slug']=='game-reward-planning')
 if i.get('execution',{}).get('pid')!=os.getpid():i.setdefault('executionHistory',[]).append(i.get('execution',{}))
 i['stage']='single-source-word-repair-candidate';i['execution']={**state,'state':STATE.relative_to(ROOT).as_posix(),'activeTasks':[{'kind':'qwen-source-word-candidate','pid':os.getpid()}] if state['gpuJobs'] else []};i['nextAction']='Read full current clothing/mask candidate ASR; preserve51 unchanged paragraphs and all seven explanations. Compose a separate voice version only after direct candidate/source review.';i['updatedAt']=now();q['updatedAt']=now();write(QUEUE,q);write(BASE/'latest-checkpoint.json',{'slug':'game-reward-planning','stage':i['stage'],'execution':i['execution'],'nextAction':i['nextAction'],'finalVideoComplete':False})
save();streak=0
while streak<3:
 line=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).splitlines()[0];free,util=[int(x.strip()) for x in line.split(',')]
 qwen=subprocess.check_output(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match 'python' -and $_.ProcessId -ne "+str(os.getpid())+" -and $_.CommandLine -match 'render_narration|render-actions|render-repair|generate_sample'}).Count"],text=True).strip()
 ready=free>=9000 and util<=35 and qwen=='0';streak=streak+1 if ready else 0;state['gpuObservations'].append({'at':now(),'freeMiB':free,'utilizationPercent':util,'otherQwenProcesses':qwen,'eligible':ready});save()
 if streak<3:time.sleep(15)
state.update(status='synthesizing-one-reviewed-source-paragraph',gpuJobs=1);save();stdout=sys.stdout;stderr=sys.stderr
class Tee:
 def __init__(self,file):self.file=file
 def write(self,text):stdout.write(text);stdout.flush();self.file.write(text);self.file.flush();return len(text)
 def flush(self):stdout.flush();self.file.flush()
with (WORK/'tts.log').open('w',encoding='utf8') as log:
 sys.stdout=Tee(log);sys.stderr=sys.stdout
 try:
  sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as rn
  rn.configure_project('game-reward-planning',manifest_override=request['manifest']);rn.load_tts_dependencies();items=rn.build_render_items(rn.load_jobs());assert len(items)==1;rn.render_chunks(items,batch_size=1)
  for sid,h in request['originalWavLocks'].items():assert sha(ROOT/request['originalWavDirectory']/(sid+'-scene.wav'))==h
  state.update(status='source-paragraph-candidate-finished-asr-pending',endedAt=now(),exitCode=0,gpuJobs=0);save()
 except BaseException:
  state.update(status='source-paragraph-candidate-failed',endedAt=now(),exitCode=1,gpuJobs=0,error=traceback.format_exc());save();traceback.print_exc();raise
 finally:sys.stdout=stdout;sys.stderr=stderr
