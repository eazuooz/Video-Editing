"""One new full take plus its complete adjacent paragraph; CPU2/GPU0."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,sys
os.environ['CUDA_VISIBLE_DEVICES']='-1';os.environ['OMP_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
STATE=BASE/'native-onset-asr-execution-v131.json';FOLDER=BASE/'local/native-onset-asr-v131'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
def write(p,j):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.writing-'+str(os.getpid()));tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
def main():
 execution=BASE/'native-onset-execution-v128.json';e=read(execution);request=BASE/'native-onset-request-v128.json';r=read(request)
 if STATE.exists() or e.get('exitCode')!=0 or not e['generationComplete'] or e['requestSha256']!=sha(request):raise RuntimeError('Completed current take required; preserve prior results')
 h=read(ROOT/'shared/output/gpu-handoff'/f"{e['leaseToken']}.json")
 if h.get('state')!='research_resume_verified':raise RuntimeError('Actual research restoration required')
 lease=ROOT/'shared/output/GPU_HANDOFF.json'
 if lease.exists() and read(lease).get('token')==e['leaseToken']:raise RuntimeError('Own lease remains active')
 take=e['results'][0];s=read(ROOT/r['script']['path'])['scenes'][0]
 if len(e['results'])!=1 or s['id']!='capture-target-view' or not take['technicalTailGatePassed'] or sha(ROOT/take['path'])!=take['sha256']:raise RuntimeError('One unchanged accepted take required')
 fresh=dict(id=s['id'],path=take['path'],sha256=take['sha256'],sampleRange=[0,take['samples']],ko=s['ko'],en=s['en'])
 assembly=read(BASE/'additive-unmixed-review-assembly-v2.json');entry=next(x for x in assembly['entries'] if x['id']==s['insertAfter'])
 previous=dict(id=entry['id'],path=assembly['audio']['path'],sha256=assembly['audio']['sha256'],sampleRange=[entry['startSample'],entry['endSample']],ko=entry['text'],en=entry['en'])
 jobs=[dict(label='whole-capture-target-view',mode='whole',sources=[fresh]),dict(label='context-capture-target-view',mode='independent-complete-join',sources=[previous,fresh],gapSamples=6720)]
 plan=dict(preparedAt=stamp(),execution=dict(path=rel(execution),sha256=sha(execution)),jobs=jobs,cpuThreads=2,gpuJobs=0,expectedWindows=2,expectedTextUsedAsPrompt=False,prior96WindowsRepeated=False,finalMixedAsr=False)
 if '--plan-only' in sys.argv:
  p=BASE/'native-onset-asr-plan-v131.json'
  if p.exists():raise RuntimeError('Preserve prior plan')
  write(p,plan);print('Prepared2 windows; recognition0');return
 import psutil
 me=psutil.Process();ancestors={p.pid for p in me.parents()}|{me.pid}
 if psutil.virtual_memory().available<6*1024**3:raise RuntimeError('Less than6GiB free')
 for p in psutil.process_iter(['pid','cmdline']):
  if p.pid in ancestors:continue
  try:
   cmd=' '.join(p.info['cmdline'] or []).lower()
   if 'game-lighting-history' in cmd and any(x in cmd for x in ['render-native-onset-v128.py','review-native-onset-v131.py','review-native-followup-v124.py']):raise RuntimeError('Owned exclusive worker live')
  except(psutil.NoSuchProcess,psutil.AccessDenied):pass
 state=dict(schemaVersion=1,startedAt=stamp(),actualIdentity=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd()),status='loading-one-CPU-model',plan=plan,completed=[],expectedWindows=2,cpuThreads=2,gpuJobs=0,allDirectlyReviewed=False,humanWholeListeningApproved=False,finalMixedAsr=False,uploaded=False);write(STATE,state)
 try:
  import numpy as np,soundfile as sf,torch,torchaudio
  from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
  torch.set_num_threads(2);torch.set_num_interop_threads(1)
  mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
  model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu');processor=AutoProcessor.from_pretrained(str(mp),local_files_only=True)
  recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
  for job in jobs:
   target=FOLDER/(job['label']+'.json')
   if target.exists():raise RuntimeError('Preserve existing result')
   pieces=[];ranges=[];offset=0
   for source in job['sources']:
    p=ROOT/source['path'];a,z=source['sampleRange']
    if sha(p)!=source['sha256']:raise RuntimeError('PCM changed')
    with sf.SoundFile(p) as f:
     if f.samplerate!=24000 or f.channels!=1:raise RuntimeError('PCM format changed')
     f.seek(a);part=f.read(z-a,dtype='float32')
    if len(part)!=z-a:raise RuntimeError('PCM truncated')
    if pieces:gap=job.get('gapSamples',0);pieces.append(np.zeros(gap,dtype=np.float32));offset+=gap
    ranges.append(dict(source=source,windowSampleRange=[offset,offset+len(part)],pcmFloat32Sha256=hashlib.sha256(part.tobytes()).hexdigest()));pieces.append(part);offset+=len(part)
   signal=np.concatenate(pieces);state.update(status='recognizing-one-window',current=job['label']);write(STATE,state)
   result=recognize(dict(raw=torchaudio.functional.resample(torch.from_numpy(signal),24000,16000).numpy(),sampling_rate=16000),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   for source in job['sources']:
    if sha(ROOT/source['path'])!=source['sha256']:raise RuntimeError('PCM changed during ASR')
   write(target,dict(completedAt=stamp(),job=job,sourceRanges=ranges,sampleRate=24000,samples=len(signal),pcmFloat32Sha256=hashlib.sha256(signal.tobytes()).hexdigest(),expectedTextUsedAsPrompt=False,directFullTextCompared=False,narrationApproved=False,humanWholeListeningApproved=False,finalMixedAsr=False,**result))
   state['completed'].append(dict(label=job['label'],result=rel(target),sha256=sha(target)));state.update(current=None,status='window-complete-awaiting-direct-review');write(STATE,state);print('DONE '+job['label'],flush=True)
  state.update(status='two-windows-complete-awaiting-direct-review',exitCode=0,endedAt=stamp());write(STATE,state)
 except BaseException as exc:state.update(status='failed-preserve-completed',error=repr(exc),exitCode=1,endedAt=stamp());write(STATE,state);raise
if __name__=='__main__':main()
