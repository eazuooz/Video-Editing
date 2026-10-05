"""Read all current final mixed chapters and independent ambiguous contexts on CPU."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,time,traceback
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1';DEST=W/'mixed-asr-v1';STATE=W/'mixed-asr-execution.json'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,j):
 temp=p.with_name(p.name+f'.{os.getpid()}.writing')
 for n in range(30):
  try:temp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(temp,p);return
  except PermissionError:
   if n==29:raise
   time.sleep(.1)
assert not STATE.exists() and not DEST.exists();DEST.mkdir()
plan=read(W/'plan.json');mix=W/'final-mix.wav';settings=read(W/'mix-settings.json');assert sha(mix)==settings['wavSha256']
audio,sr=sf.read(mix,dtype='float32',always_2d=True);assert sr==48000 and len(audio)==32100*800
windows=[dict(label='scene-'+s['id'],scene=s['id'],fromSeconds=s['startFrame']/60,toSeconds=(s['startFrame']+s['frames'])/60,expectedKo=[r['ko'] for r in s['speechEvidence']],scope='entire current final mixed chapter') for s in plan['scenes']]
for sid,a,z,label in [('01',5,14,'names-overview'),('02',23,32,'credit-limit'),('04',0,8,'title-movement'),('06',0,8,'curved-ice-clarity'),('10',7.5,15,'quiet-Pepper-join'),('10',15,24,'separate-water-cuts'),('12',1.5,7,'general-specific-join'),('12',20,31,'observed-cost-join'),('13',20,30.433333,'new-conditions-end'),('14',0,20,'result-distinct-rules'),('15',9,30,'desk-target-moving')]:
 s=next(s for s in plan['scenes'] if s['id']==sid);windows.append(dict(label=sid+'-'+label,scene=sid,fromSeconds=s['startFrame']/60+a,toSeconds=min((s['startFrame']+s['frames'])/60,s['startFrame']/60+z),scope='independent context; no expected text supplied to recognizer'))
write(W/'mixed-asr-request.json',dict(createdAt=now(),mixSha256=sha(mix),planSha256=sha(W/'plan.json'),windows=windows,expectedWasRecognizerPrompt=False))
state=dict(startedAt=now(),pid=os.getpid(),sessionId=None,status='loading-local-CPU-whisper',device='cpu',threads=2,mixSha256=sha(mix),totalScenes=15,totalWindows=26,completed=0,activeTasks=[],exitCode=None,automaticApproval=False,humanWholeListening='pending')
def checkpoint():
 write(STATE,state);qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(i for i in q['items'] if i['slug']=='avoid-game-comparisons');ex=item['execution'];running=state.get('exitCode') is None
 ex.update(observedAt=now(),phase='current15-final-mix-CPU-ASR',currentFinalMixAsr=dict(state=rel(STATE),**state),cpuProductionJobs=1 if running else 0,primaryCpuProductionJobs=1 if running else 0,gpuSynthesisJobs=0,renderJobs=0,uploads=0,activeTasks=[dict(kind='current-final-mix-CPU-ASR',pid=os.getpid(),state=rel(STATE))] if running else [])
 item.update(stage='current15-final-mix-CPU-ASR',updatedAt=now(),nextAction='Directly compare all15 mixed chapters and11 independent contexts, then every final caption/cut pixel and complete technical checks.');q['updatedAt']=item['updatedAt'];write(qp,q)
 for p in [BASE/'latest-checkpoint.json',ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/latest-checkpoint.json']:
  cp=read(p);cp.update(stage=item['stage'],updatedAt=item['updatedAt'],execution=ex,nextAction=item['nextAction'],finalMixComplete=True,finalMixAsrApproved=False,renderComplete=(W/'render-result.json').exists(),qaComplete=False,collected=False,privateUploadSaved=False);write(p,cp)
checkpoint();results=[]
try:
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu');processor=AutoProcessor.from_pretrained(str(mp),local_files_only=True)
 transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
 for w in windows:
  wav=DEST/(w['label']+'.wav');sf.write(wav,audio[round(w['fromSeconds']*sr):round(w['toSeconds']*sr)].mean(axis=1),sr,subtype='PCM_16');state.update(status='transcribing-'+w['label']);checkpoint()
  raw=transcriber(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},chunk_length_s=30,return_timestamps='word')
  row={**w,'windowSha256':sha(wav),'text':raw['text'],'words':raw['chunks'],'expectedWasRecognizerPrompt':False,'directReview':False};results.append(row)
  write(DEST/(w['label']+'.json'),row);state['completed']=len(results);write(DEST/'asr.json',dict(mixSha256=settings['wavSha256'],planSha256=sha(W/'plan.json'),complete=len(results)==26,results=results,humanWholeListening='pending',automaticallyApproved=False));checkpoint();print(json.dumps(dict(label=w['label'],text=row['text']),ensure_ascii=False),flush=True)
 state.update(status='closed-current-final-mix-ASR-awaiting-direct-content-review',exitCode=0,endedAt=now());checkpoint()
except BaseException:
 state.update(status='closed-current-final-mix-ASR-failed',exitCode=1,endedAt=now(),error=traceback.format_exc());checkpoint();raise
