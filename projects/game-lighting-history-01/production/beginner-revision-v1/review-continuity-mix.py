"""Recognize each current mixed chapter once, then require direct comparison."""
import pathlib,json,hashlib,datetime,os,sys,collections
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';F=P/'production/local/continuity-v2';O=F/'mixed-asr'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def wr(p,d):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 resume='--resume' in sys.argv or '--check-resume' in sys.argv
 prior=rd(O/'execution.json') if (O/'execution.json').exists() else None
 assert resume==bool(prior),'Existing results require --resume; do not repeat completed chapters.'
 import runpy
 runpy.run_path(str(pathlib.Path(__file__).with_name('production-authority.py')))['require_selected_production']()
 plan=rd(F/'plan.json');mix=rd(F/'mix-execution.json');wav=F/mix['currentWav'];assert mix['status']=='complete-awaiting-current-mixed-ASR' and mix['outputs'][wav.name]==sh(wav)
 import psutil
 state=dict(status='loading',startedAt=now(),pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cpuThreads=2,gpuJobs=1,planSha256=sh(F/'plan.json'),mixSha256=sh(wav),mixPath=wav.relative_to(R).as_posix(),expectedTextUsedAsPrompt=False,completed=[],fullDirectReviewComplete=False,humanListening='pending')
 if prior:
  assert prior['status'] in ['running','loading','interrupted-by-reboot','failed'],'Completed recognition must not be restarted.'
  assert prior['planSha256']==state['planSha256'] and prior['mixSha256']==state['mixSha256'],'Inputs changed: inspect instead of resuming.'
  # PID numbers alone are never ownership. A copied checkpoint on another
  # machine may refer to an unrelated process with the same PID.
  if psutil.pid_exists(prior['pid']):
   old=psutil.Process(prior['pid'])
   assert not (abs(old.create_time()-prior['createTime'])<.01 and old.cmdline()==prior['command']),'Original worker is still alive.'
  ids=[c['id'] for c in plan['chapters']]
  for key in ids:
   result=O/(key+'.json')
   if result.exists():
    saved=rd(result);assert saved['chapter']==key and saved['mixSha256']==state['mixSha256'] and saved.get('text') and saved.get('chunks'),key
    state['completed'].append(key)
  assert set(prior['completed'])<=set(state['completed']),'A completed result is missing; restore it first.'
  assert len(state['completed'])<len(ids),'All chapter results already exist; direct review is next.'
  state['resumedFrom']=dict(status=prior['status'],startedAt=prior['startedAt'],pid=prior['pid'],completed=state['completed'].copy())
  if '--check-resume' in sys.argv:
   print(json.dumps(dict(valid=True,completed=state['completed'],remaining=[k for k in ids if k not in state['completed']],mixSha256=state['mixSha256'],startsRecognition=False)));return
  history=O/('execution-before-resume-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json');assert not history.exists();wr(history,prior)
 import soundfile as sf,torch,torchaudio,numpy as np
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1)
 def save():wr(O/'execution.json',state)
 save()
 try:
  modelpath=pathlib.Path(os.environ.get('ASR_MODEL_PATH',str(next(pathlib.Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots').iterdir()))));model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cuda:0');proc=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
  asr=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float16,device=0)
  orig={f"{s['id']}-p{i+1}":v for s in rd(P/'script/narration.ko.json')['scenes'] for i,v in enumerate(s['lines'])}
  guides={g['id']:g['ko'] for g in rd(P/'production/native-guide-design-v2.json')['rows']}
  orig.update({r['key']:r['ko'] for r in rd(P/'production/beginner-revision-v1/changes.json')['rows'] if not r['key'].startswith('g')})
  guides.update({r['key']:r['ko'] for r in rd(P/'production/beginner-revision-v1/changes.json')['rows'] if r['key'].startswith('g')});orig.update({r['id']:r['ko'] for r in rd(P/'production/beginner-revision-v1/native-additions.json')['guideRows']})
  for row in [r for pair in rd(P/'production/beginner-revision-v1/current-policy-changes.json')['pairs'] for r in pair['rows']]:
   (guides if row['key'].startswith('g') else orig)[row['key']]=row['ko']
  state['status']='running';save()
  with sf.SoundFile(wav) as audio:
   sr=audio.samplerate;assert sr==48000
   for i,ch in enumerate(plan['audioChapterBoundaries']):
    if ch['id'] in state['completed']:continue
    end=plan['audioChapterBoundaries'][i+1]['startFrame'] if i+1<len(plan['chapters']) else plan['frames']-600
    audio.seek(ch['startFrame']*800);data=audio.read((end-ch['startFrame'])*800,dtype='float32').mean(axis=1)
    keys=[]
    for v in sorted(plan['voice'],key=lambda v:v['startFrame']):
     if ch['startFrame']<=v['startFrame']<end and (not keys or keys[-1]!=v['key']):keys.append(v['key'])
    expected=' '.join((guides if k.startswith('g') else orig)[k] for k in keys)
    result=asr(dict(raw=torchaudio.functional.resample(torch.from_numpy(data),48000,16000).numpy(),sampling_rate=16000),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
    wr(O/(ch['id']+'.json'),dict(chapter=ch['id'],startFrame=ch['startFrame'],endFrame=end,expectedKo=expected,orderedKeys=keys,mixSha256=state['mixSha256'],expectedTextUsedAsPrompt=False,directlyCompared=False,completedAt=now(),**result))
    state['completed'].append(ch['id']);save();print('DONE',ch['id'],flush=True)
  state.update(status='complete-awaiting-direct-review',endedAt=now(),exitCode=0);save()
 except BaseException as e:state.update(status='failed',error=repr(e),endedAt=now());save();raise
if __name__=='__main__':
 import uuid,psutil,subprocess,runpy
 runpy.run_path(str(pathlib.Path(__file__).with_name('production-authority.py')))['require_selected_production']()
 lease=R/'shared/output/GPU_HANDOFF.json';assert not lease.exists(),'Foreign GPU lease preserved.'
 me=psutil.Process();ancestry={p.pid for p in me.parents()}|{me.pid}
 foreign=[dict(pid=p.pid,name=p.info['name']) for p in psutil.process_iter(['pid','name']) if (p.info['name'] or '').lower().startswith(('python','train','torchrun')) and p.pid not in ancestry]
 assert not foreign,foreign
 gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).strip()
 free,util=map(int,gpu.split(','));assert free>=9000 and util<50,gpu
 token=str(uuid.uuid4());record=dict(token=token,project='game-lighting-history-01',state='gpu_granted_to_final_asr',coordinator=dict(pid=me.pid,createTime=me.create_time()),researchPaused=False,gpuBefore=gpu)
 with lease.open('x',encoding='utf8') as f:json.dump(record,f,indent=2)
 try:main()
 finally:
  if lease.exists() and rd(lease).get('token')==token:
   record.update(state='released',finishedAt=now(),researchRestarts=0);wr(F/'mixed-asr-gpu-lease.json',record);lease.unlink()
