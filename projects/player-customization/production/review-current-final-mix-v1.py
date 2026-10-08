"""Prepared single CPU2/GPU0 current mixed audio reviewer; no auto approval."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, sys, time, traceback, wave
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;FINAL=BASE/'final-v1'
DEST=FINAL/'mixed-asr-v1';STATE=FINAL/'mixed-asr-execution.json';SESSION=FINAL/'mixed-asr-session.json'
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing')
 for n in range(60):
  try:t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p);return
  except OSError:
   if n==59:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args();r=read(ROOT/a.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'].replace('Z','+00:00'))).total_seconds()<240
mix=FINAL/'final-mix.wav';settings=read(FINAL/'mix-settings.json');planPath=FINAL/'plan.json';plan=read(planPath)
mixCompleted=read(FINAL/settings.get('repairExecution','').split('/')[-1]) if settings.get('repairExecution') else read(FINAL/'mix-execution.json')
assert mixCompleted['exitCode']==0 and settings['wavSha256']==sha(mix) and settings['planSha256']==sha(planPath)
if settings.get('repairExecution'):assert mixCompleted['wavSha256']==settings['wavSha256'] and settings['allCompletedOriginalTimelineAndBgmStepsPreserved']
timingPath=ROOT/plan['voiceTiming'];assert sha(timingPath)==plan['voiceTimingSha256'];timing=read(timingPath)
koPath=ROOT/'projects/player-customization/script/narration.ko.v3.json';enPath=ROOT/'projects/player-customization/script/narration.en.v2.json'
script=read(koPath);scenes={x['id']:x for x in script['scenes']};windows=[]
contexts=[(1,3),(1,2),(3,4),(3,4),(1,2),(1,2),(1,2),(1,2),(3,4),(2,4),(3,4),(1,3),(1,2),(1,2),(2,4),(2,4)]
for row in timing['rows']:
 windows.append(dict(label='whole-'+row['id'],scene=row['id'],fromSample=row['startFrame']*800,toSample=row['endFrame']*800,
  expectedKo=scenes[row['id']]['lines'],scope='Entire current mixed chapter; comparison text never used as recognizer prompt.'))
for row,(a0,b0) in zip(timing['rows'],contexts):
 start=row['startFrame']*800+row['paragraphStartSamples'][a0-1]*2
 end=row['startFrame']*800+row['paragraphStartSamples'][b0]*2 if b0<4 else row['endFrame']*800
 windows.append(dict(label='context-'+row['id']+f'-p{a0}-{b0}',scene=row['id'],fromSample=start,toSample=end,
  expectedKo=scenes[row['id']]['lines'][a0-1:b0],scope='Independent complete paragraphs using reviewed current PCM boundaries; names/action/ending context.'))
assert len(windows)==32 and len(timing['rows'])==16
assert not STATE.exists() and not DEST.exists(),'Read completed/running checkpoint, never repeat mixed ASR.'
with wave.open(str(mix),'rb') as w:
 params=w.getparams();assert params.framerate==48000 and params.nchannels==2 and params.sampwidth==2 and params.nframes==36041*800
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
os.environ['PATH']='C:/ProgramData/HP/LCDDisplayHelper/bin'+os.pathsep+os.environ.get('PATH','')
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
DEST.mkdir();save(FINAL/'mixed-asr-request.json',dict(createdAt=now(),mixSha256=sha(mix),planSha256=sha(planPath),windows=windows,
 expectedWasRecognizerPrompt=False,totalWhole=16,totalIndependentContexts=16,allApproved=False))
s=dict(schemaVersion=1,slug='player-customization',pid=os.getpid(),sessionId=None,commandLine=[sys.executable,*sys.argv],
 startedAt=now(),status='loading-local-CPU2-whisper-current-final-mix',resourceEvidence=a.resource,cpuThreads=2,gpu=0,singleJob=True,
 mixSha256=sha(mix),planSha256=sha(planPath),koSha256=sha(koPath),enSha256=sha(enPath),total=32,completed=0,exitCode=None,
 automaticApproval=False,allWholeTextsDirectlyCompared=False,allIndependentTextsDirectlyCompared=False,finalMixedAsrApproved=False,
 humanWholeListening='pending',humanPronunciation='pending',allFinalPixels=False,collected=False,uploaded=False)
def checkpoint():
 if SESSION.exists():
  x=read(SESSION)
  if x['pid']==os.getpid():s.update(sessionId=x['sessionId'],processIdentity=x['processIdentity'])
 s['observedAt']=now();save(STATE,s)
 job=dict(status=s['status'],pid=os.getpid(),sessionId=s['sessionId'],processIdentity=s.get('processIdentity'),commandLine=s['commandLine'],
  state=rel(STATE),cpuThreads=2,gpu=0,singleJob=True,progress=dict(completed=s['completed'],total=32),exitCode=s['exitCode'],workerExpectedRunning=s['exitCode'] is None)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=s['status'],ownedJob=job,recordedAt=now(),finalMixedAsrExecution=rel(STATE),
  nextAction='Directly compare full actual texts of16current mixed chapters and16independent complete contexts with their exact PCM/expected paragraphs. Preserve errors; no ending heuristic approval. Then guarded final pair/pixels/QA/collect/private/Git.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items'] if x['slug']=='player-customization')
 i.update(stage=cp['stage'],currentExecution=job,finalMixedAsrExecution=rel(STATE),nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
try:
 checkpoint();import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1);modelPath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelPath),dtype=torch.float32,low_cpu_mem_usage=True,
  use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
 processor=AutoProcessor.from_pretrained(str(modelPath),local_files_only=True)
 transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,
  feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu');results=[]
 for window in windows:
  wav=DEST/(window['label']+'.wav')
  with wave.open(str(mix),'rb') as w:w.setpos(window['fromSample']);pcm=w.readframes(window['toSample']-window['fromSample'])
  assert len(pcm)==(window['toSample']-window['fromSample'])*4
  with wave.open(str(wav),'wb') as w:w.setparams(params);w.writeframes(pcm)
  with wave.open(str(wav),'rb') as w:assert w.readframes(w.getnframes())==pcm
  s.update(status='transcribing-current-mixed-'+window['label'],activeWindow=window['label']);checkpoint()
  raw=transcriber(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},chunk_length_s=30,return_timestamps='word')
  row={**window,'windowPath':rel(wav),'windowSha256':sha(wav),'mixPcmSliceSha256':hashlib.sha256(pcm).hexdigest(),
   'exactStereoMixSampleBytesMatched':True,'text':raw['text'],'words':raw['chunks'],'expectedWasRecognizerPrompt':False,'directReview':False}
  results.append(row);save(DEST/(window['label']+'.json'),row)
  save(DEST/'asr.json',dict(mixSha256=settings['wavSha256'],planSha256=sha(planPath),complete=len(results)==32,results=results,
   automaticApproval=False,finalMixedAsrApproved=False,humanWholeListening='pending',humanPronunciation='pending'))
  s['completed']=len(results);checkpoint();print(json.dumps(dict(label=window['label'],text=row['text']),ensure_ascii=False),flush=True)
 assert sha(mix)==settings['wavSha256'] and sha(planPath)==s['planSha256'] and sha(koPath)==s['koSha256'] and sha(enPath)==s['enSha256']
 s.update(status='closed-current-final-mixed-ASR-await-direct-comparison',exitCode=0,endedAt=now(),activeWindow=None);checkpoint()
except BaseException:
 s.update(status='closed-current-final-mixed-ASR-failed',exitCode=1,endedAt=now(),error=traceback.format_exc());checkpoint();raise
