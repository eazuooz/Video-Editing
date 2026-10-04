"""Two approved actual-commentary paragraph candidates; no automatic splice."""
import hashlib,json,os,sys,traceback,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'repair1'
now=lambda:datetime.now(timezone.utc).isoformat()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
request=read(WORK/'request.json')
for lock in request['inputLocks']:
 if sha(ROOT/lock['path'])!=lock['sha256']:raise RuntimeError('Stale patch input')
original=ROOT/'shared/output/narration/game-reward-planning/qwen3-1.7b-balanced-v1/chunks'
for sid,digest in request['originalWavLocks'].items():
 if sha(original/(sid+'-scene.wav'))!=digest:raise RuntimeError('Original PCM changed')
if (WORK/'tts-execution.json').exists():raise RuntimeError('Preserve existing candidates; inspect actual worker state')
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','game-reward-planning','--check'],cwd=ROOT,check=True)
state={'pid':os.getpid(),'startedAt':now(),'status':'running','gpuJobs':1,'scope':['02a','08b'],'log':'projects/game-reward-planning/production/repair1/tts.log','autoSplice':False,'original13WavsUnchanged':True}
def save():
 state['updatedAt']=now();(WORK/'tts-execution.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 q=read(ROOT/'production/batches/sakurai-planning-game-design/queue.json');item=next(x for x in q['items'] if x['slug']=='game-reward-planning')
 if item.get('execution',{}).get('pid')!=os.getpid():item.setdefault('executionHistory',[]).append(item.get('execution',{}))
 launch=read(WORK/'tts-launch.json') if (WORK/'tts-launch.json').exists() else {}
 item['stage']='two-paragraph-targeted-tts-repair';item['execution']={**state,'phase':item['stage'],'sessionId':launch.get('sessionId'),'state':'projects/game-reward-planning/production/repair1/tts-execution.json','activeTasks':[] if not state['gpuJobs'] else [{'kind':'qwen-targeted-repair','pid':os.getpid(),'scope':state['scope']}]}
 item['nextAction']='Directly review both current candidate ASR; preserve all original13 PCM and50 unaffected paragraphs. Apply to separate version only after source/meaning/quiet-boundary checks, then full current ASR and seam review before timing/captions.';item['updatedAt']=now()
 item['checkpoints']['narration']=False;q['updatedAt']=now();(ROOT/'production/batches/sakurai-planning-game-design/queue.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (BASE/'latest-checkpoint.json').write_text(json.dumps({'slug':'game-reward-planning','stage':item['stage'],'execution':item['execution'],'nextAction':item['nextAction'],'finalVideoComplete':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save();stdout=sys.stdout;stderr=sys.stderr
class Tee:
 def __init__(self,file):self.file=file
 def write(self,text):stdout.write(text);stdout.flush();self.file.write(text);self.file.flush();return len(text)
 def flush(self):stdout.flush();self.file.flush()
with (WORK/'tts.log').open('w',encoding='utf-8') as log:
 sys.stdout=Tee(log);sys.stderr=sys.stdout
 try:
  sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as r
  r.configure_project('game-reward-planning',manifest_override=request['manifest']);r.load_tts_dependencies();r.render_chunks(r.build_render_items(r.load_jobs()),batch_size=1)
  for sid,digest in request['originalWavLocks'].items():
   if sha(original/(sid+'-scene.wav'))!=digest:raise RuntimeError('Original PCM changed during candidate generation')
  state.update(status='finished-candidates-awaiting-full-asr',endedAt=now(),exitCode=0,gpuJobs=0);save()
 except BaseException:
  state.update(status='failed',endedAt=now(),exitCode=1,gpuJobs=0,error=traceback.format_exc());save();traceback.print_exc();raise
 finally:sys.stdout=stdout;sys.stderr=stderr
