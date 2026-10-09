"""One approved Qwen voice batch after an owned cooperative GPU handoff.

No model is loaded while waiting for another lease. The existing coordinator
restores the original research command/cwd/queue in its finally path.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse,hashlib,json,os,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
STATE=BASE/'narration-tts-execution-v1.json';REQUEST=BASE/'narration-tts-request-v1.json';SESSION=BASE/'narration-tts-session-v1.json'
now=lambda:datetime.now(timezone.utc).isoformat()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
ap=argparse.ArgumentParser();ap.add_argument('--dry-run',action='store_true');args=ap.parse_args()
request=read(REQUEST)
assert request['pairedWholeTextReview'] and request['overviewPromiseReview']
for x in request['protectedInputs']:
 if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Protected input changed: '+x['path'])
assert read(ROOT/request['scriptReview'])['contentReadyForApprovedVoiceMeasurement']
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
if STATE.exists():raise RuntimeError('Existing TTS execution: inspect real outputs; do not repeat completed voice.')
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
sys.path.insert(0,str(ROOT/'qwen3-tts'))
import render_narration as rn
rn.configure_project('presenting-game-scores');items=rn.build_render_items(rn.load_jobs())
assert {rel(x.path) for x in items}=={s['path'] for s in request['scenes']}, 'Request/renderer path disagreement before synthesis'
assert {x.text for x in items}=={s['text'] for s in request['scenes']}, 'Request/renderer text disagreement before synthesis'
if args.dry_run:
 print('Prepared10 scenes/30 paragraphs; current review and exact renderer paths match. Model/GPU/state creation0.',flush=True);raise SystemExit(0)
import psutil
me=psutil.Process()
leasePath=ROOT/'shared/output/GPU_HANDOFF.json'
ancestors={p.pid:p.create_time() for p in [me,*me.parents()]}
lease=read(leasePath) if leasePath.exists() else None
owner=lease.get('coordinator',{}) if lease else {}
owned=lease and lease.get('project')=='presenting-game-scores' and abs(ancestors.get(owner.get('pid'),-1)-owner.get('createTime',0))<.01
if not owned:
 waiting=dict(schemaVersion=1,slug='presenting-game-scores',recordedAt=now(),actualPid=me.pid,createTime=me.create_time(),
  commandLine=me.cmdline(),stage='serialized-request-waiting-before-model',modelLoaded=False,gpuJobs=0,
  foreignLease=dict(project=lease.get('project'),token=lease.get('token'),coordinator=owner,state=lease.get('state')) if lease else None,
  sessionId=read(SESSION).get('sessionId') if SESSION.exists() else None,researchPauseOrProcessChanges=0)
 save(BASE/'narration-tts-waiting-v1.json',waiting)
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff,check_gpu_handoff
check_gpu_tts_hold('presenting-game-scores','cuda:0',False)
schedule_gpu_handoff('presenting-game-scores','cuda:0',False)
check_gpu_handoff('presenting-game-scores','cuda:0',False)
lease=read(leasePath)
state=dict(schemaVersion=1,slug='presenting-game-scores',actualPid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),
 sessionId=read(SESSION).get('sessionId') if SESSION.exists() else None,startedAt=now(),stage='loading-approved-Qwen-under-owned-lease',
 device='cuda:0',cpuThreads=2,gpuJobs=1,request=rel(REQUEST),requestSha256=sha(REQUEST),leaseToken=lease['token'],
 researchCoordinator=lease.get('coordinator'),log=lease.get('ttsLog'),total=10,results=[],activeScene=None,
 generationComplete=False,exitCode=None,wholeAsrDirectReview=False,finalMixedAsrApproved=False,
 heuristicIsApproval=False,humanListening='pending',humanPronunciation='pending')
def checkpoint():
 state['updatedAt']=now();save(STATE,state)
 p=BASE/'latest-checkpoint.json';c=read(p);c.update(recordedAt=now(),stage=state['stage'] if state['exitCode'] is not None else 'single-GPU-approved-voice-measurement',ttsStarted=True,
  ownedJob=dict(pid=state['actualPid'],createTime=state['createTime'],commandLine=state['commandLine'],sessionId=state['sessionId'],
   state=rel(STATE),log=state['log'],gpu=state['gpuJobs'],cpuThreads=2,completed=len(state['results']),total=10,
   workerExpectedRunning=state['exitCode'] is None,exitCode=state['exitCode']),
  nextAction='Observe exact own lease/PID/log. After TTS exit verify original research resume, then whole current-hash ASR plus independent contexts and measured source allocation.');save(p,c)
 qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(10):
  raw=qpath.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
  item.update(stage=c['stage'],currentExecution=c['ownedJob'],ttsStarted=True,nextAction=c['nextAction']);q['updatedAt']=now()
  if qpath.read_text('utf-8-sig')==raw:save(qpath,q);break
  time.sleep(.15)
 else:raise RuntimeError('Concurrent batch writer: preserve execution and inspect queue')
checkpoint()
try:
 rn.INFERENCE_DEVICE='cuda:0';rn.load_tts_dependencies();rn.torch.set_num_threads(2);rn.torch.set_num_interop_threads(1)
 original_load=rn.Qwen3TTSModel.from_pretrained.__func__
 def load(cls,*a,**kw):kw.setdefault('attn_implementation','sdpa');return original_load(cls,*a,**kw)
 rn.Qwen3TTSModel.from_pretrained=classmethod(load)
 original_generate=rn.Qwen3TTSModel.generate_voice_clone;bytext={s['text']:s for s in request['scenes']}
 def generate(self,*a,**kw):
  s=bytext[kw['text'][0]];state.update(stage='synthesizing-'+s['id'],activeScene=s['id']);checkpoint()
  current=rn.torch.cuda.current_stream(self.device);stream=rn.torch.cuda.Stream(device=self.device,priority=-1);stream.wait_stream(current)
  with rn.torch.cuda.stream(stream):result=original_generate(self,*a,**kw)
  stream.synchronize();current.wait_stream(stream);rn.torch.cuda.empty_cache();return result
 rn.Qwen3TTSModel.generate_voice_clone=generate
 original_badness=rn._badness
 rn._badness=lambda tail,decay:original_badness(tail,decay) if rn._passes_quality(tail,decay) else 1000000+original_badness(tail,decay)
 original_write=rn.sf.write
 def write_audio(file,data,samplerate,*a,**kw):
  out=original_write(file,data,samplerate,*a,**kw);p=Path(file)
  if p.parent==rn.CHUNK_DIR and p.name.endswith('-scene.wav'):
   s=next(x for x in request['scenes'] if (ROOT/x['path']).resolve()==p.resolve())
   record=dict(id=s['id'],path=rel(p),sha256=sha(p),samples=len(data),sampleRate=samplerate,seconds=len(data)/samplerate,
    tailRatio=rn._tail_ratio(data,samplerate),tailDecayMs=rn._tail_decay_ms(data,samplerate),heuristicIsApproval=False,wholeAsrApproved=False)
   state['results']=[x for x in state['results'] if x['id']!=s['id']]+[record];checkpoint()
  return out
 rn.sf.write=write_audio
 rn.render_chunks(items,1,set());rn.assemble_outputs(rn.load_jobs())
 for x in request['protectedInputs']:
  if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Protected input changed during synthesis: '+x['path'])
 state.update(stage='ten-scenes-measured-awaiting-full-ASR',generationComplete=True,gpuJobs=0,finishedAt=now(),exitCode=0,
  totalRawSceneSeconds=sum(x['seconds'] for x in state['results']),allProtectedInputsUnchanged=True,
  provisionalNarration=dict(path=rel(rn.FINAL_WAV),sha256=sha(rn.FINAL_WAV),timing=rel(rn.TIMING_JSON),koSrt=rel(rn.FINAL_SRT),
   paragraphBoundaryMethod='quiet valleys near text weights; final direct ASR alignment pending'))
 checkpoint();print('Voice generated. Whole ASR/contexts and original research-resume verification remain pending.',flush=True)
except BaseException:
 state.update(stage='failed-voice-preserve-current-chunks',gpuJobs=0,finishedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();traceback.print_exc();raise
