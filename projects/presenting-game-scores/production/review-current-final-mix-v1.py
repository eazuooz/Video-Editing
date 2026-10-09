"""One CPU2/GPU0 ASR job: 10 mixed chapters +21 complete contexts.

Full expected text is comparison data, never an ASR prompt. No auto approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, subprocess, sys, time, traceback, wave
import psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;FINAL=BASE/'final-v1'
DEST=FINAL/'mixed-asr-v1';STATE=FINAL/'mixed-asr-execution.json';SESSION=FINAL/'mixed-asr-session.json'
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat()
rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args();r=read(ROOT/a.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
mix=FINAL/'final-mix.wav';aac=FINAL/'final-mix.m4a';settings=read(FINAL/'mix-settings.json')
completed=read(FINAL/'mix-execution.json');plan_path=FINAL/'plan.json';plan=read(plan_path)
assert completed['exitCode']==completed['outerExitCode']==0 and completed['outerExitDirectlyObserved']
assert settings['wavSha256']==sha(mix) and settings['aacSha256']==sha(aac) and settings['planSha256']==sha(plan_path)
assert plan['finalTimingApproved'] and plan['allInputSegmentCaptionPixelsReviewed'] and plan['narrationSamples']==6388323
preservation=read(FINAL/'pcm-timeline-preservation.json');assert preservation['all19CurrentPcmSamplesIdentical'] and preservation['sourceCoverageExactlyOnce']
voice=read(ROOT/plan['currentVoiceSelection']);assert voice['currentVoiceApproved']
assert sha(ROOT/plan['currentVoiceSelection'])==plan['currentVoiceSelectionSha256']
cap_path=FINAL/'captions.json';cap=read(cap_path);assert cap['allCurrentCueTextsDirectlyRead'] and cap['allInputCuePixelsReviewed']
subprocess.run(['node','scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
windows=[]
def add(label,scene,start,end,expected,independent,purpose):
 assert 48000<=start<end<=18452*400
 windows.append(dict(label=label,scene=scene,fromSample=start*2,toSample=end*2,
  padSamplesEachSide=28800 if independent else 0,expectedKo=expected,independent=independent,
  scope=purpose,expectedWasRecognizerPrompt=False))
for chapter in plan['chapters']:
 chunks=sorted([c for c in cap['chunks'] if chapter['startFrame']/60-1e-8<=c['startSeconds']<chapter['endFrameExclusive']/60-1e-8],key=lambda c:c['startSeconds'])
 assert chunks
 add('whole-'+chapter['id'],chapter['id'],chapter['startFrame']*400,chapter['endFrameExclusive']*400,
  [c['ko'] for c in chunks],False,'Entire current mixed chapter, including real observation intervals and all complete original/guide clauses.')
placements=plan['voicePlacements'];bounds=plan['paragraphBoundaries']
originals=[v for v in voice['scenes'] if v['id'] in bounds]
assert len(originals)==10
def mapped(voice_id,start,end):
 row=next(p for p in placements if p['voiceId']==voice_id and p['sourceStartSample']<=start and p['sourceEndSampleExclusive']>=end)
 return row['startSample']+start-row['sourceStartSample'],row['startSample']+end-row['sourceStartSample']
for v in originals:
 vid=v['id'];b=bounds[vid];chapter=vid[:2]
 if chapter=='01':
  start,end=mapped(vid,0,b[-1]);expected=[p['ko'] for p in cap['paragraphs'] if p['scene']==vid]
  add('context-01-overview-complete',chapter,start,end,expected,True,'Independent complete three-sentence overview, with0.6sec zero padding each side.')
 else:
  start,end=mapped(vid,b[2],b[3]);expected=[p['ko'] for p in cap['paragraphs'] if p['scene']==vid and p['paragraph']==3]
  assert len(expected)==1
  add('context-'+chapter+'-complete-p3',chapter,start,end,expected,True,'Independent entire original closing paragraph; padding contains no invented greeting or script prompt.')
guides=[v for v in voice['scenes'] if v['id'] not in bounds]
assert len(guides)==9
for v in guides:
 row=next(p for p in placements if p['voiceId']==v['id']);assert row['sourceStartSample']==0 and row['sourceEndSampleExclusive']==v['samples']
 expected=[p['ko'] for p in cap['paragraphs'] if p['scene']==v['id']];assert len(expected)==1
 add('context-'+v['id']+'-complete',v['id'],row['startSample'],row['endSampleExclusive'],expected,True,
  'Independent complete observation guide; exact mixed PCM interval,0.6sec zero padding each side.')
for index,(start,end) in enumerate([(90600,195480),(195480,302160)],1):
 a0,b0=mapped('06-relative-gap',start,end)
 expected=[c['ko'] for c in cap['chunks'] if c['scene']=='06-relative-gap' and c['paragraph']==2 and c['chunk']==index]
 assert len(expected)==1
 add(f'context-06-complete-p2-clause-{index}','06',a0,b0,expected,True,
  'Independent complete sentence of original paragraph2, separated around the two exact numeric-observation guides.')
assert len(windows)==31 and sum(w['independent'] for w in windows)==21
assert not STATE.exists() and not DEST.exists(),'Read actual running/completed ASR; never repeat.'
with wave.open(str(mix),'rb')as w:
 params=w.getparams();assert (params.framerate,params.nchannels,params.sampwidth,params.nframes)==(48000,2,2,19052*800)
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
os.environ['PATH']='C:/ProgramData/HP/LCDDisplayHelper/bin'+os.pathsep+os.environ.get('PATH','')
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
DEST.mkdir();save(FINAL/'mixed-asr-request.json',dict(createdAt=now(),mixSha256=sha(mix),aacSha256=sha(aac),
 planSha256=sha(plan_path),captionSha256=sha(cap_path),windows=windows,totalWhole=10,totalIndependentContexts=21,
 expectedWasRecognizerPrompt=False,allApproved=False,humanWholeListening='pending',humanPronunciation='pending'))
p=psutil.Process();s=dict(schemaVersion=1,slug='presenting-game-scores',pid=p.pid,createTime=p.create_time(),
 command=p.cmdline(),cwd=p.cwd(),sessionId=None,startedAt=now(),status='loading-local-CPU2-whisper-current-final-mix',
 resourceEvidence=a.resource,cpuThreads=2,gpu=0,singleJob=True,mixSha256=sha(mix),aacSha256=sha(aac),
 planSha256=sha(plan_path),captionSha256=sha(cap_path),total=31,completed=0,exitCode=None,
 automaticApproval=False,allWholeTextsDirectlyCompared=False,allIndependentTextsDirectlyCompared=False,
 finalMixedAsrApproved=False,humanWholeListening='pending',humanPronunciation='pending',allFinalPixels=False,collected=False,uploaded=False,researchControlChanges=0)
def checkpoint():
 if SESSION.exists():
  x=read(SESSION)
  if x['pid']==s['pid'] and abs(x['createTime']-s['createTime'])<.01:s['sessionId']=x['sessionId']
 s['observedAt']=now();save(STATE,s)
 job=dict(status=s['status'],pid=s['pid'],createTime=s['createTime'],command=s['command'],cwd=s['cwd'],
  sessionId=s['sessionId'],state=rel(STATE),cpuThreads=2,gpu=0,singleJob=True,
  progress=dict(completed=s['completed'],total=31),exitCode=s['exitCode'],workerExpectedRunning=s['exitCode'] is None)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=s['status'],ownedJob=job,recordedAt=now(),finalMixedAsrExecution=rel(STATE),
  nextAction='Directly compare full actual text/words of10 mixed chapters and21 independent complete contexts with expected clauses/current PCM. Preserve recognition artifacts; no ending heuristic approval. Then guarded pair/final pixels/QA/collect/private/Git.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(8):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);i=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
  i.update(stage=cp['stage'],currentExecution=job,currentJob=job,ownedJob=job,finalMixedAsrExecution=rel(STATE),nextAction=cp['nextAction']);q['updatedAt']=now()
  if qp.read_text('utf-8-sig')==raw:save(qp,q);break
 else:raise RuntimeError('Concurrent queue preserved; retry only checkpoint writing.')
try:
 checkpoint();import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1);model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,
  use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
 processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
 transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,
  feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu');results=[]
 for window in windows:
  wav=DEST/(window['label']+'.wav')
  with wave.open(str(mix),'rb')as w:w.setpos(window['fromSample']);pcm=w.readframes(window['toSample']-window['fromSample'])
  assert len(pcm)==(window['toSample']-window['fromSample'])*4
  padded=bytes(window['padSamplesEachSide']*4)+pcm+bytes(window['padSamplesEachSide']*4)
  with wave.open(str(wav),'wb')as w:w.setparams(params);w.writeframes(padded)
  with wave.open(str(wav),'rb')as w:assert w.readframes(w.getnframes())==padded
  s.update(status='transcribing-current-mixed-'+window['label'],activeWindow=window['label']);checkpoint()
  raw=transcriber(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},chunk_length_s=30,return_timestamps='word')
  row={**window,'windowPath':rel(wav),'windowSha256':sha(wav),'mixPcmSliceSha256':hashlib.sha256(pcm).hexdigest(),
   'exactStereoMixSampleBytesMatched':True,'zeroPaddingSecondsEachSide':window['padSamplesEachSide']/48000,
   'paddedPcmSha256':hashlib.sha256(padded).hexdigest(),'text':raw['text'],'words':raw['chunks'],
   'expectedWasRecognizerPrompt':False,'directReview':False}
  results.append(row);save(DEST/(window['label']+'.json'),row)
  save(DEST/'asr.json',dict(mixSha256=settings['wavSha256'],aacSha256=settings['aacSha256'],planSha256=sha(plan_path),
   complete=len(results)==31,results=results,automaticApproval=False,finalMixedAsrApproved=False,
   humanWholeListening='pending',humanPronunciation='pending'))
  s['completed']=len(results);checkpoint();print(json.dumps(dict(label=window['label'],text=row['text']),ensure_ascii=False),flush=True)
 assert sha(mix)==settings['wavSha256'] and sha(aac)==settings['aacSha256'] and sha(plan_path)==s['planSha256'] and sha(cap_path)==s['captionSha256']
 s.update(status='closed-current-final-mixed-ASR-await-direct-comparison',exitCode=0,endedAt=now(),activeWindow=None);checkpoint()
except BaseException:
 s.update(status='closed-current-final-mixed-ASR-failed',exitCode=1,endedAt=now(),error=traceback.format_exc());checkpoint();raise
