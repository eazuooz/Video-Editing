"""Only five affected windows; reuse all69 unchanged recognition results."""
from pathlib import Path
from datetime import datetime,timezone
import os,json,hashlib
os.environ['CUDA_VISIBLE_DEVICES']='-1';os.environ['OMP_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.now(timezone.utc).isoformat()
def write(p,j):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.writing-'+str(os.getpid()));t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def main():
 statepath=BASE/'part1-onset-replacement-asr-execution-v209.json';folder=BASE/'local/part1-onset-replacement-asr-v209'
 if statepath.exists():raise RuntimeError('Preserve actual worker/results')
 old=read(BASE/'part1-selected-actions-asr-execution-v182.json');reqpath=BASE/'part1-selected-current-tts-request-v208.json';req=read(reqpath);selectedpath=BASE/'part1-selected-current-tts-execution-v208.json';selected=read(selectedpath)
 if old.get('exitCode')!=0 or len(old['completed'])!=74 or selected['requestSha256']!=sha(reqpath) or not selected['generationComplete']:raise RuntimeError('Closed74 and selected current37 required')
 if read(ROOT/'shared/output/gpu-handoff'/(selected['leaseToken']+'.json'))['state']!='research_resume_verified':raise RuntimeError('Actual GPU return required')
 for x in req['protectedInputs']:
  if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Changed protected input '+x['path'])
 fresh={x['id']:x for x in selected['results']};labels=req['replacementAsrLabels'];jobs=[]
 if labels!=['whole-runtime-texture-size','context-runtime-texture-size','context-ordinary-streaming-budget','whole-geometry-car-material','context-geometry-car-material']:raise RuntimeError('Exact five scope required')
 for label in labels:
  job=json.loads(json.dumps(next(x for x in old['plan']['jobs'] if x['label']==label)))
  for s in job['sources']:
   if s['id'] in ['runtime-texture-size','geometry-car-material']:
    r=fresh[s['id']];s.update(path=r['path'],sha256=r['sha256'],sampleRange=[0,r['samples']])
  jobs.append(job)
 import psutil
 own=psutil.Process();ancestors={p.pid for p in own.parents()}|{own.pid}
 if psutil.virtual_memory().available<6*1024**3:raise RuntimeError('Insufficient free RAM')
 for p in psutil.process_iter(['pid','name','cmdline']):
  if p.pid in ancestors:continue
  try:
   command=' '.join(p.info['cmdline'] or []).lower()
   if 'game-lighting-history' in command and ('ffmpeg' in (p.info['name'] or '').lower() or any(x in command for x in ['review-part1-selected-actions-v182.py','review-part1-onset-replacements-v209.py','render-part1-onset-repairs-v199.py'])):raise RuntimeError('Another owned media worker is alive')
  except (psutil.NoSuchProcess,psutil.AccessDenied):pass
 plan=dict(selected=dict(path=selectedpath.relative_to(ROOT).as_posix(),sha256=sha(selectedpath)),oldExecution=dict(path='projects/game-lighting-history-04/production/part1-selected-actions-asr-execution-v182.json',sha256=sha(BASE/'part1-selected-actions-asr-execution-v182.json')),jobs=jobs,expectedWindows=5,reusedUnchangedWindows=69,expectedTextUsedAsPrompt=False)
 state=dict(startedAt=stamp(),actualIdentity=dict(pid=own.pid,createTime=own.create_time(),command=own.cmdline(),cwd=own.cwd()),status='loading-one-CPU-model',plan=plan,expectedWindows=5,completed=[],cpuThreads=2,gpuJobs=0,allDirectlyReviewed=False,finalMixedAsr=False,uploaded=False);write(statepath,state)
 try:
  import soundfile as sf,numpy as np,torch,torchaudio
  from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
  torch.set_num_threads(2);torch.set_num_interop_threads(1);mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
  model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu');processor=AutoProcessor.from_pretrained(str(mp),local_files_only=True)
  recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
  for job in jobs:
   parts=[];ranges=[];offset=0;target=folder/(job['label']+'.json')
   if target.exists():raise RuntimeError('Preserve completed result')
   for source in job['sources']:
    file=ROOT/source['path'];a,z=source['sampleRange']
    if sha(file)!=source['sha256']:raise RuntimeError('Changed source PCM')
    with sf.SoundFile(file) as f:
     if f.samplerate!=24000 or f.channels!=1:raise RuntimeError('Unexpected source format')
     f.seek(a);part=f.read(z-a,dtype='float32')
    if len(part)!=z-a:raise RuntimeError('Truncated source PCM')
    if parts:
     gap=job.get('gapSamples',0);parts.append(np.zeros(gap,dtype=np.float32));offset+=gap
    ranges.append(dict(id=source['id'],windowSampleRange=[offset,offset+len(part)],source=source,pcmFloat32Sha256=hashlib.sha256(part.tobytes()).hexdigest()));parts.append(part);offset+=len(part)
   signal=np.concatenate(parts);state.update(status='recognizing-one-window',current=job['label']);write(statepath,state)
   opts=dict(generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   if job['mode']=='whole':opts.update(chunk_length_s=30,stride_length_s=5)
   result=recognize(dict(raw=torchaudio.functional.resample(torch.from_numpy(signal),24000,16000).numpy(),sampling_rate=16000),**opts)
   for source in job['sources']:
    if sha(ROOT/source['path'])!=source['sha256']:raise RuntimeError('Changed PCM during recognition')
   record=dict(completedAt=stamp(),job=job,sourceRanges=ranges,sampleRate=24000,samples=len(signal),pcmFloat32Sha256=hashlib.sha256(signal.tobytes()).hexdigest(),expectedTextUsedAsPrompt=False,directFullTextCompared=False,narrationApproved=False,humanWholeListeningApproved=False,finalMixedAsr=False,**result);write(target,record)
   state['completed'].append(dict(label=job['label'],result=target.relative_to(ROOT).as_posix(),sha256=sha(target)));state.update(status='window-complete-awaiting-direct-review',current=None);write(statepath,state);print('DONE '+job['label']+' '+str(len(state['completed']))+'/5',flush=True)
  state.update(status='five-replacement-windows-complete-awaiting-direct-review',endedAt=stamp(),exitCode=0,current=None);write(statepath,state)
 except BaseException as exc:
  state.update(status='failed-preserve-results',error=repr(exc),endedAt=stamp(),exitCode=1);write(statepath,state);raise
if __name__=='__main__':main()
