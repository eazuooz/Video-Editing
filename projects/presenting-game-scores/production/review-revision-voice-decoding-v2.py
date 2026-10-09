"""CPU2/GPU0 unprompted beam5 of four unresolved revision contexts; no approval."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,subprocess,sys,time,traceback
import psutil
ROOT=Path(__file__).resolve().parents[3];CPBASE=Path(__file__).parent;BASE=CPBASE/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
def now():return datetime.now(timezone.utc).isoformat()
def save(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
STATE=BASE/'voice-decoding-asr-execution-v2.json';SESSION=STATE.with_name(STATE.stem+'.session.json');LOG=BASE/'voice-decoding-asr-v2.log';DEST=BASE/'voice-decoding-asr-v2'
assert not STATE.exists() and not DEST.exists() and not LOG.exists(),'Inspect actual existing diagnostic; do not repeat.'
resource=read(ROOT/args.resource);assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
for mode in ['whole','contexts','joined']:
 s=read(BASE/f'voice-{mode}-asr-execution-v1.json');assert s['exitCode']==0 and s['actualExitObserved']
restored=read(BASE/'research-handoff-verification-v2.json');assert restored['restorationVerified'] and restored['ownedCoordinatorClosed']
for row in read(BASE/'narration-tts-request-v1.json')['protectedInputs']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
plan=read(BASE/'voice-decoding-asr-plan-v2.json');reviewp=ROOT/plan['priorReview'];assert sha(reviewp)==plan['priorReviewSha256'] and read(reviewp)['allFiveCompleteJoinedContextsDirectlyCompared']
inputs=plan['inputs'];assert len(inputs)==4
for x in inputs:assert sha(ROOT/x['sourcePath'])==x['sourceSha256']
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
process=psutil.Process();DEST.mkdir()
state=dict(schemaVersion=1,slug='presenting-game-scores',pid=process.pid,createTime=process.create_time(),
 processIdentity=dict(pid=process.pid,createTime=process.create_time(),commandLine=process.cmdline(),cwd=process.cwd()),
 sessionId=None,startedAt=now(),status='loading-unprompted-beam5-CPU2',completed=0,total=4,cpuThreads=2,gpuJobs=0,cpuJobs=1,
 resource=resource,inputs=inputs,priorDirectReview=rel(reviewp),priorDirectReviewSha256=sha(reviewp),
 decoding=dict(num_beams=5,do_sample=False,language='korean',task='transcribe',expectedWasRecognizerPrompt=False),
 actualExitObserved=False,exitCode=None,automaticApproval=False,currentVoiceApproved=False,finalMixedAsrApproved=False,
 humanListening='pending',humanPronunciation='pending',researchProcessOrControlChanges=0)
def checkpoint():
 if SESSION.exists():
  launch=read(SESSION)
  if launch['pid']==process.pid:state['sessionId']=launch['sessionId']
 state['updatedAt']=now();save(STATE,state)
 job=dict(status=state['status'],processIdentity=state['processIdentity'],pid=process.pid,sessionId=state['sessionId'],
  state=rel(STATE),log=rel(LOG),startedAt=state['startedAt'],completed=state['completed'],total=4,cpuThreads=2,gpu=0,
  singleJob=True,workerExpectedRunning=state['exitCode'] is None,exitCode=state['exitCode'])
 cpp=CPBASE/'latest-checkpoint.json';cp=read(cpp);cp.update(recordedAt=now(),stage='revision-unprompted-beam5-CPU-ASR-v2',ownedJob=job,
  currentVoiceApproved=False,asrApproved=False,narrationApproved=False,
  nextAction='Read all four complete beam5 results and current PCM against the preserved greedy results. No new synthesis or research control; measured candidate is prepared only and all final gates remain false.');save(cpp,cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(8):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='presenting-game-scores');item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction']);q['updatedAt']=now();q['lastProgressAt']=now()
  if qp.read_text('utf-8-sig')==raw:save(qp,q);break
  time.sleep(.15)
 else:raise RuntimeError('Concurrent batch mutation; preserve foreign work.')
class Tee:
 def __init__(self,o,f):self.o=o;self.f=f
 def write(self,s):self.o.write(s);self.o.flush();self.f.write(s);self.f.flush();return len(s)
 def flush(self):self.o.flush();self.f.flush()
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8');oldout,olderr=sys.stdout,sys.stderr
with LOG.open('x',encoding='utf-8') as log:
 sys.stdout=Tee(oldout,log);sys.stderr=sys.stdout
 try:
  checkpoint()
  import torch
  from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
  torch.set_num_threads(2);torch.set_num_interop_threads(1)
  path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
  model=AutoModelForSpeechSeq2Seq.from_pretrained(str(path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
  processor=AutoProcessor.from_pretrained(str(path),local_files_only=True)
  transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
  results=[]
  for x in inputs:
   state['status']='beam5-current-'+x['id'];checkpoint();p=ROOT/x['sourcePath'];assert sha(p)==x['sourceSha256']
   out=transcriber(str(p),generate_kwargs={'language':'korean','task':'transcribe','num_beams':5,'do_sample':False},return_timestamps='word')
   assert sha(p)==x['sourceSha256']
   result={**x,'text':out['text'],'words':out['chunks'],'audioSha256':sha(p),'expectedWasRecognizerPrompt':False,'decoding':state['decoding'],'directReview':False,'approved':False}
   results.append(result);save(DEST/(x['id']+'.json'),result);save(DEST/'asr.json',dict(complete=len(results)==4,results=results,automaticApproval=False))
   state['completed']=len(results);checkpoint();print(json.dumps(dict(id=x['id'],text=result['text']),ensure_ascii=False),flush=True)
  state.update(status='closed-beam5-awaiting-direct-review',exitCode=0,cpuJobs=0,finishedAt=now());checkpoint()
 except BaseException:
  state.update(status='closed-beam5-failed',exitCode=1,cpuJobs=0,finishedAt=now(),error=traceback.format_exc());checkpoint();traceback.print_exc();raise
 finally:sys.stdout,sys.stderr=oldout,olderr
