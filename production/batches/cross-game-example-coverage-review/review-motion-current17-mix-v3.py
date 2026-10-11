"""CPU2 current decoded AAC: whole17 then independent81, without expected prompts."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,subprocess,sys,traceback,wave
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
os.environ['PATH']='C:/ProgramData/HP/LCDDisplayHelper/bin;'+os.environ['PATH']
import psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();now=lambda:datetime.now(timezone.utc).isoformat()
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,o):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);ap.add_argument('--mode',choices=['whole','contexts'],required=True);args=ap.parse_args()
mode=args.mode;sp=R/f'current17-mixed-{mode}-asr-execution-v3.json';dest=R/f'current17-mixed-{mode}-asr-v3';logpath=R/f'current17-mixed-{mode}-asr-v3.log'
audiofolder=ROOT/f'shared/output/cross-game-example-coverage/motion/current17-mixed-{mode}-asr-v3'
assert not any(x.exists() for x in [sp,dest,logpath,audiofolder]),'Preserve completed or running slices/models.'
resource=read(ROOT/args.resource);assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
assert resource['ownHeavyCpuJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
subprocess.run([NODE,'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT,check=True)
mix=read(R/'current-mix-execution-v2.json');ms=read(R/'current-mix-execution-v2.session.json')
assert mix['actualExitCode']==ms['actualOuterExitCode']==0 and ms['workerCurrentlyAlive']==False
assert mix['all17RawPcmPlacementsExact'] and mix['all71ProtectedInputsUnchanged']
for x in mix['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
source=ROOT/mix['decodedAac'];assert sha(source)==mix['decodedAacSha256']
plan=read(R/'measured-current17-plan-v2.json');assert sha(R/'measured-current17-plan-v2.json')==mix['planSha256']
with wave.open(str(source),'rb') as w:
 wp=w.getparams();count=w.getnframes();assert wp.framerate==48000 and wp.nchannels==2 and wp.sampwidth==2 and count==plan['totalFrames']*800
inputs=[]
if mode=='whole':
 adds={x['id']:x['lines'] for x in read(R/'script/additions.ko.json')['scenes']}
 for s in plan['scenes']:
  expected=adds.get(s['id']) or [p['ko'] for p in plan['baselinePlan']['paragraphs'] if p['scene']==s['id']]
  assert expected
  inputs.append(dict(id=s['id'],scene=s['id'],sourcePath=rel(source),sourceSha256=sha(source),startSample=s['startFrame']*800,endSample=s['endFrame']*800,zeroPaddingSamplesEachSide=14400,expectedKo=expected,sourceOriginalPcmSha256=s['audioSha256']))
 assert len(inputs)==17
else:
 context=read(R/'current17-mixed-independent-context-plan-v2.json');review=read(ROOT/context['wholeReview'])
 assert sha(ROOT/context['wholeReview'])==context['wholeReviewSha256'] and review['all17WholeTextsDirectlyCompared']
 assert context['currentWholeWordsAndPcmBoundariesDirectlyCompared'] and context['sourceSha256']==sha(source)
 inputs=context['contexts'];assert len(inputs)==81
me=psutil.Process();ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
dest.mkdir();audiofolder.mkdir(parents=True)
state=dict(schemaVersion=1,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,mode=mode,startedAt=now(),status='preparing-current17-mixed-slices',resource=resource,total=len(inputs),completed=0,results=[],cpuThreads=2,cpuJobs=1,gpuJobs=0,exitCode=None,mixWavSha256=mix['mixWavSha256'],mixAacSha256=mix['mixAacSha256'],decodedAacSha256=sha(source),expectedWasRecognizerPrompt=False,automaticallyApproved=False,currentMixedAudioApproved=False,humanListeningApproved=False,humanPronunciationApproved=False,researchManipulations=0)
def checkpoint():
 ss=sp.with_name(sp.stem+'.session.json')
 if ss.exists():
  v=read(ss);assert v['pid']==me.pid and abs(v['createTime']-me.create_time())<.01;state['sessionId']=v['sessionId']
 state['updatedAt']=now();save(sp,state)
 cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],activeOwnedWorkers=0 if state['exitCode'] is not None else 1,currentMixedAudioApproved=False,ownedJob=dict(active=state['exitCode'] is None,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=state['sessionId'],state=rel(sp),log=rel(logpath),completed=state['completed'],total=len(inputs),cpuThreads=2,gpuJobs=0,exitCode=state['exitCode']),next='Directly compare whole17 current mixed texts; prepare/review complete independent81 boundaries from current words and exact PCM mapping. Then final captions/pair/pixels; no upload before QA.')
 save(R/'latest-checkpoint.json',cp)
 qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
 for v in q.values():
  if isinstance(v,dict) and str(v.get('currentCheckpoint','')).endswith('revision-cross-game-four-v1/latest-checkpoint.json'):v.update(activeOwnedWorkers=cp['activeOwnedWorkers'],currentMixedAsrExecution=rel(sp))
 q.update(recordedAt=now(),next=cp['next']);assert qp.read_text('utf-8-sig')==raw;save(qp,q)
class Tee:
 def __init__(self,out,file):self.out=out;self.file=file
 def write(self,s):self.out.write(s);self.out.flush();self.file.write(s);self.file.flush();return len(s)
 def flush(self):self.out.flush();self.file.flush()
with logpath.open('x',encoding='utf-8') as log:
 original=sys.stdout;olderr=sys.stderr;sys.stdout=Tee(original,log);sys.stderr=sys.stdout
 try:
  checkpoint();sliced=[]
  with wave.open(str(source),'rb') as w:
   for row in inputs:
    a,b=row['startSample'],row['endSample'];assert 0<=a<b<=count;w.setpos(a);pcm=w.readframes(b-a);assert len(pcm)==(b-a)*4
    pad=row['zeroPaddingSamplesEachSide'];data=b'\0'*(pad*4)+pcm+b'\0'*(pad*4);target=audiofolder/(row['id']+'.wav')
    with wave.open(str(target),'wb') as x:x.setparams(wp);x.writeframes(data)
    with wave.open(str(target),'rb') as x:assert x.readframes(x.getnframes())==data
    sliced.append({**row,'contextPath':rel(target),'contextSha256':sha(target),'sourceSlicePcmSha256':hashlib.sha256(pcm).hexdigest(),'exactSourceStereoPcmBytesMatched':True})
  assert sha(source)==mix['decodedAacSha256'];save(dest/'pcm-slices.json',dict(slices=sliced,sourceSha256=sha(source)))
  import torch
  from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
  torch.set_num_threads(2);torch.set_num_interop_threads(1);modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
  state['status']='loading-current17-mixed-CPU2-whisper';checkpoint()
  model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
  processor=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
  transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
  for row in sliced:
   state['status']='transcribing-current17-mixed-'+row['id'];checkpoint();p=ROOT/row['contextPath'];assert sha(p)==row['contextSha256']
   raw=transcriber(str(p),generate_kwargs={'language':'korean','task':'transcribe'},chunk_length_s=30,return_timestamps='word')
   result={**row,'text':raw['text'],'words':raw['chunks'],'expectedWasRecognizerPrompt':False,'directReview':False,'approved':False}
   assert sha(p)==row['contextSha256'];save(dest/(row['id']+'.json'),result);state['results'].append(result);state['completed']=len(state['results'])
   save(dest/'asr.json',dict(complete=len(state['results'])==len(inputs),results=state['results'],decodedAacSha256=sha(source),mixAacSha256=mix['mixAacSha256'],automaticApproval=False));checkpoint();print(json.dumps(dict(id=row['id'],text=result['text']),ensure_ascii=False),flush=True)
  for x in mix['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
  assert sha(source)==mix['decodedAacSha256'];state.update(status=f'current17-mixed-{mode}-ASR-closed-awaiting-direct-review',exitCode=0,cpuJobs=0,finishedAt=now());checkpoint()
 except BaseException:
  state.update(status=f'failed-current17-mixed-{mode}-ASR-preserve-files',exitCode=1,cpuJobs=0,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
 finally:sys.stdout=original;sys.stderr=olderr
