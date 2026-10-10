"""Generate only two reviewed complete replacement paragraphs under owned lease.

The original scripts and all twelve PCM files are immutable. The established
coordinator completes current research then restores its exact command/cwd.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
FOLDER=BASE/'voice-clarity-v2';STATE=FOLDER/'execution.json';REQUEST=FOLDER/'request.json';SESSION=FOLDER/'session.json'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
rel=lambda p:p.resolve().relative_to(ROOT).as_posix()
def save(p,x):
 temp=p.with_name(p.name+f'.{os.getpid()}.writing');temp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(temp,p)
ap=argparse.ArgumentParser();ap.add_argument('--dry-run',action='store_true');args=ap.parse_args()
request=read(REQUEST)
assert request['total']==request['completeParagraphs']==2
assert sha(ROOT/request['review'])==request['reviewSha256']
assert read(ROOT/request['review'])['contentReadyForApprovedVoiceMeasurement']
assert not STATE.exists() and not any((ROOT/s['path']).exists() for s in request['scenes']), 'Inspect existing execution/output; never repeat completed synthesis'
for row in request['protectedInputs']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
sys.path.insert(0,str(ROOT/'qwen3-tts'))
import render_narration as rn
rn.configure_project('character-parameters')
rn.CHUNK_DIR=ROOT/'shared/output/narration/character-parameters/voice-clarity-v2'
items=[rn.RenderItem(key=s['id'],text=s['text'],path=ROOT/s['path']) for s in request['scenes']]
assert all(i.path.parent==rn.CHUNK_DIR for i in items)
if args.dry_run:
 print('Prepared two complete paragraphs; unchanged baseline twelve PCM/script/source hashes. Model/state/GPU0.',flush=True);raise SystemExit(0)
import psutil
me=psutil.Process();leasePath=ROOT/'shared/output/GPU_HANDOFF.json'
ancestors={p.pid:p.create_time() for p in [me,*me.parents()]}
lease=read(leasePath) if leasePath.exists() else None
owner=lease.get('coordinator',{}) if lease else {}
owned=lease and lease.get('project')=='character-parameters' and abs(ancestors.get(owner.get('pid'),-1)-owner.get('createTime',0))<.01
if not owned:
 save(FOLDER/'waiting.json',dict(recordedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),stage='serialized-two-paragraph-request-before-model',modelLoaded=False,gpuJobs=0,foreignLease=lease,sessionId=read(SESSION).get('sessionId') if SESSION.exists() else None,processOrResearchControlChangesByWrapper=0))
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff,check_gpu_handoff
check_gpu_tts_hold('character-parameters','cuda:0',False)
schedule_gpu_handoff('character-parameters','cuda:0',False)
check_gpu_handoff('character-parameters','cuda:0',False)
lease=read(leasePath)
state=dict(schemaVersion=1,slug='character-parameters',actualPid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=read(SESSION).get('sessionId') if SESSION.exists() else None,startedAt=now(),stage='loading-approved-Qwen-two-complete-paragraphs',device='cuda:0',cpuThreads=2,gpuJobs=1,request=rel(REQUEST),requestSha256=sha(REQUEST),leaseToken=lease['token'],researchCoordinator=lease.get('coordinator'),log=lease.get('ttsLog'),total=2,results=[],generationComplete=False,exitCode=None,actualExitObserved=False,currentVoiceApproved=False,finalMixedAsrApproved=False,heuristicIsApproval=False,candidateAdopted=False,humanListening='pending',humanPronunciation='pending')
def checkpoint():
 state['updatedAt']=now();save(STATE,state)
 cpPath=BASE/'latest-checkpoint.json';cp=read(cpPath)
 cp.update(recordedAt=now(),stage=state['stage'],narrationApproved=False,asrApproved=False,voiceMeasured=False,voiceClarityRequest=rel(REQUEST),ownedJob=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),sessionId=state['sessionId'],state=rel(STATE),log=state['log'],gpu=state['gpuJobs'],cpuThreads=2,completed=len(state['results']),total=2,workerExpectedRunning=state['exitCode'] is None,exitCode=state['exitCode']),nextAction='Observe exact own lease. After actual outer exit verify original research resume, then fresh whole/independent complete paragraph ASR before candidate adoption. Preserve original12 PCM and all final gates.');save(cpPath,cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(10):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(i for i in q['items'] if i['slug']=='character-parameters')
  item.update(stage=cp['stage'],currentExecution=cp['ownedJob'],voiceClarityRequest=rel(REQUEST),nextAction=cp['nextAction']);item['checkpoints']['narration']=False;q['updatedAt']=now()
  if qp.read_text('utf-8-sig')==raw:save(qp,q);break
  time.sleep(.15)
 else:raise RuntimeError('Concurrent queue update; preserve foreign bytes and inspect')
checkpoint()
try:
 rn.INFERENCE_DEVICE='cuda:0';rn.load_tts_dependencies();rn.torch.set_num_threads(2);rn.torch.set_num_interop_threads(1)
 original_load=rn.Qwen3TTSModel.from_pretrained.__func__
 def load(cls,*a,**kw):kw.setdefault('attn_implementation','sdpa');return original_load(cls,*a,**kw)
 rn.Qwen3TTSModel.from_pretrained=classmethod(load)
 original_generate=rn.Qwen3TTSModel.generate_voice_clone;bytext={s['text']:s for s in request['scenes']}
 def generate(self,*a,**kw):
  s=bytext[kw['text'][0]];state.update(stage='synthesizing-'+s['id']);checkpoint()
  current=rn.torch.cuda.current_stream(self.device);stream=rn.torch.cuda.Stream(device=self.device,priority=-1);stream.wait_stream(current)
  with rn.torch.cuda.stream(stream):result=original_generate(self,*a,**kw)
  stream.synchronize();current.wait_stream(stream);rn.torch.cuda.empty_cache();return result
 rn.Qwen3TTSModel.generate_voice_clone=generate
 original_badness=rn._badness
 rn._badness=lambda tail,decay:original_badness(tail,decay) if rn._passes_quality(tail,decay) else 1000000+original_badness(tail,decay)
 original_write=rn.sf.write
 def write_audio(file,data,samplerate,*a,**kw):
  out=original_write(file,data,samplerate,*a,**kw);p=Path(file)
  if p.parent==rn.CHUNK_DIR and p.name.endswith('-clarity.wav'):
   s=next(s for s in request['scenes'] if (ROOT/s['path']).resolve()==p.resolve())
   r=dict(id=s['id'],path=rel(p),sha256=sha(p),samples=len(data),sampleRate=samplerate,seconds=len(data)/samplerate,tailRatio=rn._tail_ratio(data,samplerate),tailDecayMs=rn._tail_decay_ms(data,samplerate),heuristicIsApproval=False,wholeAsrApproved=False)
   state['results']=[r0 for r0 in state['results'] if r0['id']!=s['id']]+[r];checkpoint()
  return out
 rn.sf.write=write_audio
 rn.render_chunks(items,1,set())
 assert len(state['results'])==2
 for row in request['protectedInputs']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
 state.update(stage='two-paragraphs-generated-awaiting-research-resume-and-fresh-ASR',generationComplete=True,gpuJobs=0,finishedAt=now(),exitCode=0,totalReplacementSeconds=sum(r['seconds'] for r in state['results']),allProtectedBaselineInputsUnchanged=True)
 checkpoint();print('Two replacement paragraphs generated. Original12 PCM unchanged; actual research resume and fresh ASR remain pending.',flush=True)
except BaseException:
 state.update(stage='failed-two-paragraph-voice-preserve-all-takes',gpuJobs=0,finishedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();traceback.print_exc();raise
