"""Independent CPU-only readback of completed, log-confirmed changed takes.

One Whisper model, two CPU threads, batch one. No prompt from the expected
script, no TTS, no GPU, no rewriting of earlier audio or ASR evidence.
"""
from pathlib import Path
import argparse,os,json,hashlib,re,time,gc,difflib,sys,atexit
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',TOKENIZERS_PARALLELISM='false')
import psutil,soundfile as sf
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local/asr-changed';SOURCE=H/'narration/source-verified-revisions.json'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rel(p):return Path(p).absolute().relative_to(R).as_posix()
def save(p,j):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_suffix(p.suffix+'.'+str(os.getpid())+'.pending');temp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf8')
 for attempt in range(50):
  try:os.replace(temp,p);return
  except PermissionError:
   if attempt==49:raise
   time.sleep(.1)
def norm(text):return ''.join(c.lower()for c in text if c.isalnum())
def jobs():
 s=read(SOURCE);mapping={(q['episode'],q['sentence']):q for q in read(H/'narration/released-tts-map.json')['entries']};out=[]
 for e in s['episodes']:
  assert e['id']!='A03'
  for c in e['changes']+[q for q in s['existingApprovedChanges']if q['episode']==e['id']]:
   old=e['id']=='A10';m=mapping.get((e['id'],c['id']))
   if m and(m.get('ko')!=c['ko']or m.get('en')!=c['en']or m.get('text')!=c.get('spokenKo',c['ko'])):m=None
   key=('A10S'+c['id'])if old else(m['key']if m else e['id']+'S'+c['id']+'X'+hashlib.sha256(c.get('spokenKo',c['ko']).encode()).hexdigest()[:10])
   out.append({'episode':e['id'],'sentenceId':c['id'],'key':key,'expected':c['ko'],'expectedEnglish':c['en'],
    'wav':H/('local/voice/chunks'if old else'local/voice-reviewed/chunks')/(key+'-scene.wav'),
    'log':H/('local/tts-cpu.log'if old else'local/tts-reviewed-cpu.log'),'sourceRevisionsSha256':sha(SOURCE)})
 return out
def ready(job):
 f=job['wav'];logs=[job['log']]
 if job['episode']!='A10':logs += [H/'local'/name for name in ('tts-reviewed-final.log','tts-reviewed-final-cpu-fallback.log','tts-reviewed-final-gpu.log')]
 if not f.exists()or time.time()-f.stat().st_mtime<3:return None
 # Logs can be extended while read. Only a completed Rendered line is evidence.
 hits=[]
 for log in sorted([p for p in logs if p.exists()],key=lambda p:p.stat().st_mtime):
  if not log.exists():continue
  states=[x for x in log.read_text('utf8',errors='replace').splitlines()if re.match(r'^(Rendered|Checked) '+re.escape(job['key'])+r'-scene\b',x)]
  if states:
   hits.append((log,states[-1]))
 if not hits:return None
 log,line=hits[-1]
 if not line.startswith('Rendered '):return None
 info=sf.info(f)
 if info.frames<=info.samplerate*.15:return None
 return {'audioSha256':sha(f),'rate':info.samplerate,'samples':info.frames,'duration':info.duration,'completedLogLine':line,
  'logPath':rel(log),'logSnapshotSha256':sha(log)}
def compare(job,result):
 a,b=norm(job['expected']),norm(result['text']);matcher=difflib.SequenceMatcher(None,a,b,autojunk=False)
 return {'episode':job['episode'],'sentenceId':job['sentenceId'],'key':job['key'],'expected':job['expected'],'recognized':result['text'],
  'sequenceRatio':matcher.ratio(),'differences':[{'kind':tag,'expected':a[i:j],'recognized':b[k:l],'expectedCharRange':[i,j],'recognizedCharRange':[k,l]}for tag,i,j,k,l in matcher.get_opcodes()if tag!='equal'],
  'normalizedTextExact':a==b,'humanListening':False,'semanticReview':'pending-model-text-review'if a!=b else'exact-normalized-independent-readback'}
def authorize():
 c=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert c['fullLocalProductionAuthorized']and c['renderAuthorized'];return c
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--watch',action='store_true');ap.add_argument('--final-aac',action='store_true',help='Reuse this same model for changed passages of completed final AAC masters');ap.add_argument('--idle-seconds',type=int,default=900);ap.add_argument('--max-minutes',type=int,default=360);args=ap.parse_args();authorize();L.mkdir(parents=True,exist_ok=True)
 lock=L/'worker.lock.json'
 if lock.exists():
  old=read(lock)
  if psutil.pid_exists(old['pid']):raise RuntimeError('An existing ASR worker is alive; preserve it')
  lock.rename(L/('worker-stopped-'+str(old['pid'])+'.json'))
 with lock.open('x',encoding='utf8')as f:json.dump({'pid':os.getpid(),'device':'cpu','threads':2,'batchSize':1,'started':time.time()},f)
 def cleanup():
  if lock.exists()and read(lock)['pid']==os.getpid():lock.unlink()
 atexit.register(cleanup);recognize=None;model=None;processor=None;start=last=time.time();known={};memoryWaitPrinted=False
 while True:
  authorize();todo=jobs();done=[];waiting=[];worked=False
  for job in todo:
   if (L/'stop-after-current.json').exists():print('Stopped at a persisted take boundary by scoped local request',flush=True);return
   proof=ready(job)
   if proof is None:waiting.append(job['key']);continue
   out=L/'raw'/(job['key']+'.'+proof['audioSha256'][:12]+'.json')
   if out.exists():result=read(out);assert result['audio_sha256']==proof['audioSha256']
   else:
    if recognize is None:
     available=psutil.virtual_memory().available
     if available<5.5*1024**3:
      if not memoryWaitPrinted:print('CPU model waiting for5.5GiB available RAM; preserving all other jobs',flush=True);memoryWaitPrinted=True
      waiting.append(job['key']);continue
     import torch
     from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
     torch.set_num_threads(2);torch.set_num_interop_threads(1)
     modeldir=R/'qwen3-tts/models/whisper-large-v3-turbo'
     if not modeldir.exists():
      from huggingface_hub import snapshot_download
      modeldir=Path(snapshot_download('openai/whisper-large-v3-turbo',local_files_only=True))
     print('Loading one local Whisper-large-v3-turbo CPU model;2threads,batch1',flush=True)
     model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modeldir),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
     processor=AutoProcessor.from_pretrained(str(modeldir),local_files_only=True)
     recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
    save(L/'worker-state.json',{'pid':os.getpid(),'state':'recognizing','key':job['key'],'audioSha256':proof['audioSha256'],'device':'cpu'})
    print('ASR',job['key'],f"{proof['duration']:.2f}s",flush=True)
    raw=recognize(str(job['wav']),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word',batch_size=1)
    if sha(job['wav'])!=proof['audioSha256']:
     print('Take changed during readback; discarded unsaved stale result',job['key'],flush=True);waiting.append(job['key']);del raw;gc.collect();continue
    result={'episode':job['episode'],'sentenceId':job['sentenceId'],'key':job['key'],'audio':rel(job['wav']),'audio_sha256':proof['audioSha256'],
     'model':'local whisper-large-v3-turbo','device':'cpu','threads':2,'batchSize':1,'timestampMode':'word','expectedTextPromptSupplied':False,
     'text':raw['text'],'chunks':raw.get('chunks',[]),'completionEvidence':proof,'duration':proof['duration'],'humanListening':False}
    save(out,result);worked=True;last=time.time();print('READBACK',job['key'],raw['text'],flush=True);del raw;gc.collect()
   comparison=compare(job,result);comparison.update(audioSha256=proof['audioSha256'],asrPath=rel(out),asrSha256=sha(out));done.append(comparison)
   save(L/'worker-state.json',{'pid':os.getpid(),'state':'persisted-take-boundary','key':job['key'],'currentPassCompleted':len(done),'device':'cpu'})
  save(L/'index.json',{'sourceRevisionsSha256':sha(SOURCE),'status':'complete-readback-text-review-pending'if len(done)==len(todo)else'completed-takes-readback-in-progress',
   'expectedPassages':len(todo),'completedPassages':len(done),'waitingKeys':waiting,'entries':done,'gpuUsed':False,'cpuThreads':2,'modelsLoaded':1 if recognize else 0,'humanListening':False})
  print('INDEX',len(done),'/',len(todo),'waiting',len(waiting),flush=True)
  # This stays sequential with recognition, so there is no extra model/worker.
  # A pending semantic difference never becomes accepted just through polling.
  import sync_changed_audio
  sync_changed_audio.synchronize(todo,done,ready)
  raw_complete=len(done)==len(todo)
  if raw_complete and args.final_aac:
   # A final phase is deliberately part of this finite worker: no second model.
   if recognize is None:
    # A restarted worker can have every raw result cached; load on the next
    # requested final task using the same bounded model initializer below.
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    from huggingface_hub import snapshot_download
    if psutil.virtual_memory().available<5.5*1024**3:
     print('Final AAC waiting for CPU model RAM',flush=True);time.sleep(20);continue
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    modeldir=Path(snapshot_download('openai/whisper-large-v3-turbo',local_files_only=True))
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modeldir),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
    processor=AutoProcessor.from_pretrained(str(modeldir),local_files_only=True)
    recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
   import asr_final_aac
   final_complete,final_progress=asr_final_aac.run_once(recognize,todo,lambda:(L/'stop-after-current.json').exists())
   if final_progress:last=time.time()
   if final_complete:break
  elif raw_complete or not args.watch:break
  if time.time()-last>args.idle_seconds or time.time()-start>args.max_minutes*60:print('Bounded watcher stopped; resume uses matching hashes',flush=True);break
  time.sleep(20)
 print('CPU readback worker finished; source WAVs untouched',flush=True)
if __name__=='__main__':main()
