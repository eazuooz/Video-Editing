"""One CPU2 Whisper worker for changed voice or complete independent contexts.

No expected narration is passed to the recognizer. All results need direct review.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,subprocess,sys,time,traceback,wave
import psutil
ROOT=Path(__file__).resolve().parents[3];CPBASE=Path(__file__).parent;BASE=CPBASE/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['whole','contexts','joined'],required=True);ap.add_argument('--resource',required=True);ap.add_argument('--dry-run',action='store_true');a=ap.parse_args()
resource=read(ROOT/a.resource);assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
tts=read(BASE/'narration-tts-execution-v2.json');assert tts['exitCode']==0 and tts['generationComplete'] and tts['actualExitObserved'] and len(tts['results'])==11
resume=read(BASE/'research-handoff-verification-v2.json');assert resume['restorationVerified'] and resume['ownedCoordinatorClosed'] and resume['ttsLeaseToken']==tts['leaseToken']
request=read(BASE/'narration-tts-request-v1.json')
for r in request['protectedInputs']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
statePath=BASE/f'voice-{a.mode}-asr-execution-v1.json';dest=BASE/f'voice-{a.mode}-asr-v1';logPath=BASE/f'voice-{a.mode}-asr-v1.log';session=BASE/f'voice-{a.mode}-asr-session-v1.json'
assert not statePath.exists() and not dest.exists() and not logPath.exists(),'Inspect existing completed/running ASR; do not repeat'
inputs=[]
if a.mode=='whole':
 for r in request['scenes']:
  current=next(x for x in tts['results'] if x['id']==r['id']);assert sha(ROOT/current['path'])==current['sha256']
  inputs.append(dict(id=r['id'],sourcePath=current['path'],sourceSha256=current['sha256'],samples=current['samples'],seconds=current['seconds'],expectedKo=r['text']))
else:
 plan=read(BASE/f'voice-{a.mode}-asr-plan-v1.json');whole=read(BASE/'voice-whole-asr-execution-v1.json');assert whole['exitCode']==0 and whole['actualExitObserved']
 review=ROOT/plan['wholeDirectReview'];assert sha(review)==plan['wholeDirectReviewSha256'] and read(review)['allWholeTextsDirectlyCompared']
 assert plan['boundariesDirectlyComparedWithCurrentWordsAndPcm'];inputs=plan['inputs'];assert len(inputs)>=11 if a.mode=='contexts' else len(inputs)>=5
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
if a.dry_run:print('Current PCM hashes, original research restoration and recognizer input gates passed; model0.');raise SystemExit(0)
for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
dest.mkdir();me=psutil.Process();state=dict(schemaVersion=1,startedAt=now(),status='loading-CPU2-current-revision-voice-ASR',actualPid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,mode=a.mode,cpuThreads=2,cpuJobs=1,gpuJobs=0,total=len(inputs),completed=0,audioInputs=inputs,automaticApproval=False,wholeDirectReview=False,finalMixedAsrApproved=False,exitCode=None,humanListening='pending',humanPronunciation='pending')
def checkpoint():
 if session.exists():state['sessionId']=read(session)['sessionId']
 state['updatedAt']=now();save(statePath,state)
 cpPath=CPBASE/'latest-checkpoint.json';cp=read(cpPath);job=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=state['sessionId'],state=rel(statePath),log=rel(logPath),cpuThreads=2,gpu=0,completed=state['completed'],total=state['total'],workerExpectedRunning=state['exitCode'] is None,exitCode=state['exitCode'])
 cp.update(recordedAt=now(),stage='revision-current-voice-'+a.mode+'-ASR',ownedJob=job,nextAction='Read every complete current recognized passage against expected whole text and complete context; numerical/word-ending alternatives remain review material. Preserve actual research restoration and final mixed-ASR/final pixel gates.');save(cpPath,cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(8):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='presenting-game-scores');item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction']);q.update(updatedAt=now(),lastProgressAt=now())
  if qp.read_text('utf-8-sig')==raw:save(qp,q);break
  time.sleep(.15)
 else:raise RuntimeError('Concurrent queue update; preserve foreign bytes')
class Tee:
 def __init__(self,s,f):self.s=s;self.f=f
 def write(self,x):self.s.write(x);self.s.flush();self.f.write(x);self.f.flush();return len(x)
 def flush(self):self.s.flush();self.f.flush()
sys.stdout.reconfigure(encoding='utf-8');oldout=sys.stdout
with logPath.open('x',encoding='utf-8') as log:
 sys.stdout=Tee(oldout,log)
 try:
  checkpoint()
  if a.mode=='contexts':
   d=ROOT/f'shared/output/presenting-game-scores/revision-balatro60-v2/voice-contexts-v1';assert not d.exists();d.mkdir(parents=True);sliced=[]
   for r in inputs:
    src=ROOT/r['sourcePath'];assert sha(src)==r['sourceSha256']
    with wave.open(str(src),'rb') as w:
     params=w.getparams();assert params.framerate==24000 and params.nchannels==1 and params.sampwidth==2
     start,end=r['startSample'],r['endSample'];assert 0<=start<end<=w.getnframes();w.setpos(start);pcm=w.readframes(end-start)
    pad=r.get('zeroPaddingSamplesEachSide',0);padded=b'\x00\x00'*pad+pcm+b'\x00\x00'*pad;target=d/(r['id']+'.wav')
    with wave.open(str(target),'wb') as w:w.setparams(params);w.writeframes(padded)
    sliced.append({**r,'contextPath':rel(target),'contextSha256':sha(target),'exactSourceSampleBytesMatched':True,'pcmSha256':hashlib.sha256(pcm).hexdigest()})
   inputs=sliced;save(dest/'pcm-slices.json',dict(slices=sliced))
  import torch
  from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
  torch.set_num_threads(2);torch.set_num_interop_threads(1)
  modelPath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
  model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelPath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
  processor=AutoProcessor.from_pretrained(str(modelPath),local_files_only=True)
  transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
  results=[]
  for row in inputs:
   state['status']='transcribing-'+row['id'];checkpoint();p=ROOT/row.get('contextPath',row['sourcePath']);digest=row.get('contextSha256',row['sourceSha256']);assert sha(p)==digest
   raw=transcriber(str(p),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   result={**row,'text':raw['text'],'words':raw['chunks'],'audioSha256':digest,'expectedWasRecognizerPrompt':False,'directReview':False,'approved':False};assert sha(p)==digest
   results.append(result);save(dest/(row['id']+'.json'),result);save(dest/'asr.json',dict(complete=len(results)==len(inputs),results=results,automaticApproval=False))
   state['completed']=len(results);checkpoint();print(json.dumps(dict(id=row['id'],text=result['text']),ensure_ascii=False),flush=True)
  state.update(status='closed-current-revision-ASR-awaiting-direct-review',exitCode=0,cpuJobs=0,finishedAt=now());checkpoint()
 except BaseException:
  state.update(status='closed-current-revision-ASR-failed',exitCode=1,cpuJobs=0,finishedAt=now(),error=traceback.format_exc());checkpoint();traceback.print_exc();raise
 finally:sys.stdout=oldout
