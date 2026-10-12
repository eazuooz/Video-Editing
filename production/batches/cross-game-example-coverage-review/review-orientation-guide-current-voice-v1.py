"""Single CPU2 job for candidate or current byte-preserving splice/complete seam."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,os,psutil,traceback,sys
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();now=lambda:datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,x):
 t=p.with_name(p.name+'.'+str(os.getpid())+'.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);ap.add_argument('--mode',choices=['candidate','spliced'],required=True);a=ap.parse_args()
resource=read(ROOT/a.resource);assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
tts=read(O/'narration-07b-guide-repair-execution-v1.json');closure=read(O/'07b-guide-repair-voice-closure-verification-v1.json')
assert tts['actualExitObserved'] and tts['actualOuterExitCode']==0 and tts['generationComplete'] and closure['restorationVerified']
planp=O/f'guide-{a.mode}-voice-review-plan-v1.json';plan=read(planp);assert len(plan['inputs'])==(1 if a.mode=='candidate' else 2)
sp=O/f'guide-{a.mode}-voice-asr-execution-v1.json';out=O/f'guide-{a.mode}-voice-asr-v1';assert not sp.exists() and not out.exists();out.mkdir()
class Tee:
 def __init__(self,stream,log):self.stream=stream;self.log=log
 def write(self,value):self.stream.write(value);self.log.write(value);self.log.flush();return len(value)
 def flush(self):self.stream.flush();self.log.flush()
logfile=(out/'asr.log').open('w',encoding='utf-8',buffering=1)
sys.stdout=Tee(sys.stdout,logfile);sys.stderr=Tee(sys.stderr,logfile)
protected=tts['protectedInputs']+tts['results']+plan['inputs']
for x in protected:assert sha(ROOT/x['path'])==x['sha256']
me=psutil.Process();me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
s=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,startedAt=now(),mode=a.mode,cpuThreads=2,cpuJobs=1,gpuJobs=0,plan=rel(planp),planSha256=sha(planp),resource=a.resource,total=len(plan['inputs']),completed=0,results=[],status='loading-CPU2-guide-current-review',exitCode=None,expectedWasRecognizerPrompt=False,automaticApproval=False,humanListeningApproved=False,finalMixedApproved=False)
def checkpoint():
 session=sp.with_name(sp.stem+'.session.json')
 if session.exists():s['sessionId']=read(session)['sessionId']
 s['updatedAt']=now();save(sp,s)
 cp=read(O/'latest-checkpoint.json');job=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=s['sessionId'],state=rel(sp),log=rel(out/'asr.log'),cpuThreads=2,gpuJobs=0,completed=s['completed'],total=s['total'],exitCode=s['exitCode']);cp.update(recordedAt=now(),stage=s['status'],ownedJob=job,activeOwnedWorkers=s['cpuJobs'],next='Actual closure then directly compare every full expected/current text and all first/last words. Candidate and spliced currentwhole/seam approval are distinct; no human/finalmix approval.');save(O/'latest-checkpoint.json',cp)
 qp=B/'queue.json';raw=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=s['status'],ownedJob=job,activeOwnedWorkers=s['cpuJobs'],next=cp['next']);q['updatedAt']=now();assert qp.read_bytes()==raw;save(qp,q)
checkpoint()
try:
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1);modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu');proc=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True);pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float32,device='cpu')
 for row in plan['inputs']:
  s['status']='transcribing-'+row['id'];checkpoint();assert sha(ROOT/row['path'])==row['sha256']
  raw=pipe(str(ROOT/row['path']),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
  r={**row,**raw,'expectedWasRecognizerPrompt':False,'directReview':False};s['results'].append(r);s['completed']=len(s['results']);save(out/(row['id']+'.json'),r);checkpoint();print(json.dumps(dict(id=row['id'],text=r['text']),ensure_ascii=False),flush=True)
 for x in protected:assert sha(ROOT/x['path'])==x['sha256']
 s.update(status='guide-current-ASR-closed-awaiting-directcomparison',cpuJobs=0,exitCode=0,finishedAt=now());checkpoint()
except BaseException:
 s.update(status='failed-preserve-guide-current-ASR',cpuJobs=0,exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
