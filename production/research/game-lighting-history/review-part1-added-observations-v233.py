"""Recognize only the two new full paragraphs and two complete independent contexts."""
from pathlib import Path
from datetime import datetime,timezone
import os,json,hashlib,subprocess
os.environ['CUDA_VISIBLE_DEVICES']='-1';os.environ['OMP_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.now(timezone.utc).isoformat()
def save(p,j):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.writing-'+str(os.getpid()));t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def main():
 import psutil
 ep=B/'part1-added-observations-tts-execution-v232.json';e=read(ep)
 assert e.get('exitCode')==0 and e['generationComplete'] and len(e['results'])==2
 assert read(ROOT/'shared/output/gpu-handoff'/(e['leaseToken']+'.json'))['state']=='research_resume_verified'
 sp=B/'part1-added-observations-asr-execution-v233.json';assert not sp.exists()
 script=read(ROOT/'projects/game-lighting-history-04/script/physical-part1-added-observations.koen.v232.json')['scenes']
 old=read(B/'part1-selected-current-tts-execution-v219.json')['results'];oldscript=read(ROOT/'projects/game-lighting-history-04/script/physical-part1-guided-actions.koen.v175.json')['scenes']
 sources=[];jobs=[]
 def src(t,text):
  assert sha(ROOT/t['path'])==t['sha256'];return dict(id=t['id'],path=t['path'],sha256=t['sha256'],sampleRange=[0,t['samples']],ko=text)
 for s,t in zip(script,e['results']):
  assert s['id']==t['id'];new=src(t,s['ko']);previous=s['insertAfter'];p=src(next(x for x in old if x['id']==previous),next(x['ko']for x in oldscript if x['id']==previous))
  jobs.append(dict(label='whole-'+s['id'],mode='whole',sources=[new],gapSamples=0))
  jobs.append(dict(label='context-'+s['id'],mode='context',sources=[p,new],gapSamples=7200))
 me=psutil.Process();assert psutil.virtual_memory().available>6*1024**3
 state=dict(startedAt=stamp(),actualIdentity=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd()),status='loading-one-CPU-model',expectedWindows=4,completed=[],plan=dict(jobs=jobs,expectedTextUsedAsPrompt=False),cpuThreads=2,gpuJobs=0,allDirectlyReviewed=False,finalMixedAsr=False,uploaded=False);save(sp,state)
 try:
  import soundfile as sf,numpy as np,torch,torchaudio
  from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
  torch.set_num_threads(2);torch.set_num_interop_threads(1);mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
  model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu');proc=AutoProcessor.from_pretrained(str(mp),local_files_only=True)
  recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float32,device='cpu')
  for job in jobs:
   parts=[];ranges=[];offset=0;target=B/'local/part1-added-observations-asr-v233'/(job['label']+'.json');assert not target.exists()
   for s in job['sources']:
    assert sha(ROOT/s['path'])==s['sha256'];v,sr=sf.read(ROOT/s['path'],dtype='float32');assert sr==24000 and len(v)==s['sampleRange'][1]
    if parts:parts.append(np.zeros(job['gapSamples'],dtype=np.float32));offset+=job['gapSamples']
    ranges.append(dict(id=s['id'],windowSampleRange=[offset,offset+len(v)],source=s,pcmFloat32Sha256=hashlib.sha256(v.tobytes()).hexdigest()));parts.append(v);offset+=len(v)
   signal=np.concatenate(parts);state.update(status='recognizing-one-window',current=job['label']);save(sp,state)
   opts=dict(generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   if job['mode']=='whole':opts.update(chunk_length_s=30,stride_length_s=5)
   r=recognize(dict(raw=torchaudio.functional.resample(torch.from_numpy(signal),24000,16000).numpy(),sampling_rate=16000),**opts)
   save(target,dict(completedAt=stamp(),job=job,sourceRanges=ranges,sampleRate=24000,samples=len(signal),pcmFloat32Sha256=hashlib.sha256(signal.tobytes()).hexdigest(),expectedTextUsedAsPrompt=False,directFullTextCompared=False,narrationApproved=False,humanWholeListeningApproved=False,finalMixedAsr=False,**r))
   state['completed'].append(dict(label=job['label'],result=target.relative_to(ROOT).as_posix(),sha256=sha(target)));state.update(status='window-complete-awaiting-direct-review',current=None);save(sp,state);print('DONE '+job['label'],flush=True)
  state.update(status='four-new-windows-complete-awaiting-direct-review',endedAt=stamp(),exitCode=0);save(sp,state)
 except BaseException as ex:
  state.update(status='failed-preserve-results',endedAt=stamp(),exitCode=1,error=repr(ex));save(sp,state);raise
if __name__=='__main__':main()
