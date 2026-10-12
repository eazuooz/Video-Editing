"""One CPU2/GPU0 recognizer:37 whole additions and37 complete contexts.

Protected111 paragraphs are only complete adjacent context, never regenerated.
No expected text is given to recognition. Completion is not direct approval.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,sys
os.environ['CUDA_VISIBLE_DEVICES']='-1'
os.environ['OMP_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
STATE=BASE/'part1-selected-actions-asr-execution-v182.json'
FOLDER=BASE/'local/part1-selected-actions-asr-v182'
stamp=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
rel=lambda p:p.relative_to(ROOT).as_posix()
def write(p,j):
 p.parent.mkdir(parents=True,exist_ok=True)
 tmp=p.with_name(p.name+'.writing-'+str(os.getpid()))
 tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
def main():
 resume='--resume' in sys.argv;plan_only='--plan-only' in sys.argv
 if STATE.exists() and not resume and not plan_only:raise RuntimeError('Preserve existing ASR; inspect real worker before scoped resume')
 reqpath=BASE/'part1-selected-current-tts-request-v181.json';req=read(reqpath)
 scriptpath=ROOT/'projects/game-lighting-history-04/script/physical-part1-guided-actions.koen.v175.json';script=read(scriptpath)
 ttspath=(ROOT/sys.argv[sys.argv.index('--execution')+1]).resolve() if '--execution' in sys.argv else BASE/'part1-selected-current-tts-execution-v181.json'
 ttspath.relative_to(BASE);tts=read(ttspath)
 if tts.get('requestSha256')!=sha(reqpath):raise RuntimeError('Selected execution is not bound to current37 request')
 if req['script']['path']!=rel(scriptpath) or req['script']['sha256']!=sha(scriptpath):raise RuntimeError('Current corrected full37 script mismatch')
 assemblypath=BASE/'additive-unmixed-review-assembly-v2.json';assembly=read(assemblypath)
 if len(req['scenes'])!=37 or len(script['scenes'])!=37 or len(tts.get('results',[]))!=37 or not tts.get('generationComplete') or tts.get('exitCode')!=0:raise RuntimeError('All37 actual technical takes required')
 historypath=ROOT/'shared/output/gpu-handoff'/(tts['leaseToken']+'.json');history=read(historypath)
 if history.get('state')!='research_resume_verified':raise RuntimeError('Actual research restoration required before CPU recognition')
 lease=ROOT/'shared/output/GPU_HANDOFF.json'
 if lease.exists() and read(lease).get('token')==tts['leaseToken']:raise RuntimeError('Own GPU lease remains active')
 for x in req['protectedInputs']:
  if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Protected input changed: '+x['path'])
 if sha(ROOT/assembly['audio']['path'])!=assembly['audio']['sha256']:raise RuntimeError('Retained111 PCM changed')
 takes={r['id']:r for r in tts['results']}
 fresh={}
 for s in script['scenes']:
  r=takes[s['id']]
  if not r['technicalTailGatePassed'] or sha(ROOT/r['path'])!=r['sha256']:raise RuntimeError('Changed or technically unaccepted take: '+s['id'])
  fresh[s['id']]=dict(id=s['id'],path=r['path'],sha256=r['sha256'],sampleRange=[0,r['samples']],ko=s['ko'],en=s['en'],kind='new-guided')
 scenes=list(script['scenes']);additional_bindings=None
 def previous(identifier):
  if identifier in fresh:return fresh[identifier]
  e=next((e for e in assembly['entries'] if e['id']==identifier),None)
  if e is None:raise RuntimeError('Missing complete preceding context: '+identifier)
  return dict(id=e['id'],path=assembly['audio']['path'],sha256=assembly['audio']['sha256'],sampleRange=[e['startSample'],e['endSample']],ko=e['text'],en=e['en'],kind='retained-complete-neighbour')
 jobs=[]
 for s in scenes:
  jobs.append(dict(label='whole-'+s['id'],mode='whole',sources=[fresh[s['id']]]))
  jobs.append(dict(label='context-'+s['id'],mode='independent-complete-join',sources=[previous(s['insertAfter']),fresh[s['id']]],gapSamples=6720))
 expected_windows=len(jobs)
 plan=dict(physicalPart='game-lighting-history-04-1',preparedAt=stamp(),request=dict(path=rel(reqpath),sha256=sha(reqpath)),script=dict(path=rel(scriptpath),sha256=sha(scriptpath)),tts=dict(path=rel(ttspath),sha256=sha(ttspath)),researchHistory=dict(path=rel(historypath),sha256=sha(historypath)),assembly=dict(path=rel(assemblypath),sha256=sha(assemblypath)),additionalObservationBindings=additional_bindings,jobs=jobs,expectedWindows=expected_windows,cpuThreads=2,gpuJobs=0,expectedTextUsedAsPrompt=False,original111AsrRepeated=False,allDirectlyReviewed=False,finalMixedAsr=False)
 if plan_only:
  target=BASE/'part1-selected-actions-asr-plan-v182.json'
  if target.exists():raise RuntimeError('Preserve existing plan')
  write(target,plan);print('Prepared'+str(expected_windows)+' windows; no model or recognition started');return
 import psutil
 own=psutil.Process();ancestors={p.pid for p in own.parents()}|{own.pid}
 if psutil.virtual_memory().available<6*1024**3:raise RuntimeError('Less than6GiB free; model not started')
 for proc in psutil.process_iter(['pid','name','cmdline']):
  if proc.pid in ancestors:continue
  try:
   d=proc.info;c=' '.join(d['cmdline'] or []).lower()
   if 'game-lighting-history' in c and ('ffmpeg' in (d['name'] or '').lower() or any(n in c for n in ['review-part1-selected-actions-v182.py','review-part1-guided-actions-v172.py','render-part1-guided-actions-v169.py','render-part1-scoped-repair-v176.py'])):raise RuntimeError('Own media/ASR/TTS worker still live')
  except (psutil.NoSuchProcess,psutil.AccessDenied):pass
 state=dict(schemaVersion=1,startedAt=stamp(),actualIdentity=dict(pid=own.pid,createTime=own.create_time(),command=own.cmdline(),cwd=own.cwd()),status='loading-one-CPU-model',plan=plan,expectedWindows=expected_windows,completed=[],cpuThreads=2,gpuJobs=0,allDirectlyReviewed=False,humanWholeListeningApproved=False,finalMixedAsr=False,uploaded=False)
 if resume:
  prior=read(STATE)
  if not prior.get('endedAt'):raise RuntimeError('Observe ended previous worker before resume')
  identity=prior.get('actualIdentity',{})
  if psutil.pid_exists(identity.get('pid',-1)):
   old=psutil.Process(identity['pid'])
   if abs(old.create_time()-identity.get('createTime',0))<0.001 and old.cmdline()==identity.get('command'):
    raise RuntimeError('Recorded previous worker is still alive; do not duplicate recognition')
  for done in prior['completed']:
   target=ROOT/done['result'];record=read(target)
   if sha(target)!=done['sha256'] or record['job']!=next(j for j in jobs if j['label']==done['label']):raise RuntimeError('Completed result or source changed')
  state['completed']=prior['completed'];state['previousRuns']=prior.get('previousRuns',[])+[dict(actualIdentity=prior['actualIdentity'],startedAt=prior['startedAt'],endedAt=prior['endedAt'],exitCode=prior['exitCode'],completed=len(prior['completed']))]
 write(STATE,state)
 try:
  import soundfile as sf,numpy as np,torch,torchaudio
  from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
  torch.set_num_threads(2);torch.set_num_interop_threads(1)
  model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
  model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu')
  processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
  recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
  for job in jobs:
   if any(d['label']==job['label'] for d in state['completed']):continue
   target=FOLDER/(job['label']+'.json')
   if target.exists():raise RuntimeError('Preserve existing result')
   parts=[];ranges=[];offset=0
   for source in job['sources']:
    file=ROOT/source['path'];first,last=source['sampleRange']
    if sha(file)!=source['sha256']:raise RuntimeError('PCM changed before recognition')
    with sf.SoundFile(file) as f:
     if f.samplerate!=24000 or f.channels!=1:raise RuntimeError('PCM format changed')
     f.seek(first);part=f.read(last-first,dtype='float32')
    if len(part)!=last-first:raise RuntimeError('Truncated PCM')
    if parts:
     gap=job.get('gapSamples',0);parts.append(np.zeros(gap,dtype=np.float32));offset+=gap
    ranges.append(dict(id=source['id'],windowSampleRange=[offset,offset+len(part)],source=source,pcmFloat32Sha256=hashlib.sha256(part.tobytes()).hexdigest()));parts.append(part);offset+=len(part)
   signal=np.concatenate(parts);state.update(status='recognizing-one-window',current=job['label']);write(STATE,state)
   opts=dict(generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   if job['mode']=='whole':opts.update(chunk_length_s=30,stride_length_s=5)
   result=recognize(dict(raw=torchaudio.functional.resample(torch.from_numpy(signal),24000,16000).numpy(),sampling_rate=16000),**opts)
   for source in job['sources']:
    if sha(ROOT/source['path'])!=source['sha256']:raise RuntimeError('PCM changed during recognition')
   record=dict(completedAt=stamp(),job=job,sourceRanges=ranges,sampleRate=24000,samples=len(signal),pcmFloat32Sha256=hashlib.sha256(signal.tobytes()).hexdigest(),expectedTextUsedAsPrompt=False,directFullTextCompared=False,narrationApproved=False,humanWholeListeningApproved=False,finalMixedAsr=False,**result)
   write(target,record);state['completed'].append(dict(label=job['label'],result=rel(target),sha256=sha(target)));state.update(current=None,status='window-complete-awaiting-direct-review');write(STATE,state)
   print('DONE '+job['label']+' '+str(len(state['completed']))+'/'+str(expected_windows),flush=True)
  state.update(status=str(expected_windows)+'-windows-complete-awaiting-direct-full-text-review',endedAt=stamp(),exitCode=0,current=None);write(STATE,state)
 except BaseException as exc:
  state.update(status='failed-preserve-completed-results',endedAt=stamp(),exitCode=1,error=repr(exc));write(STATE,state);raise
if __name__=='__main__':main()
