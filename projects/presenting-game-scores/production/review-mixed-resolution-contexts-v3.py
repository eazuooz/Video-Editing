"""One targeted CPU2 diagnostic on unchanged current mixed PCM, no text prompt.

Three predefined complete contexts address observed decoding ambiguities. This
does not rerun the completed31-window batch or approve any result automatically.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, subprocess, time, wave
import psutil
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent; W=BASE/'final-v1'
D=W/'mixed-resolution-contexts-v3'; STATE=W/'mixed-resolution-execution-v3.json'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
r=read(ROOT/a.resource);assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
asr=read(W/'mixed-asr-execution.json');assert asr['outerExitCode']==asr['exitCode']==0 and asr['outerExitDirectlyObserved']
progress=read(W/'mixed-asr-direct-progress.json');assert progress['directlyRead']==31
mix=W/'final-mix.wav';settings=read(W/'mix-settings.json');plan=read(W/'plan.json');cap=read(W/'captions.json')
assert sha(mix)==settings['wavSha256']==progress['currentMixedAudioSha256']
assert sha(W/'plan.json')==settings['planSha256'];assert not D.exists() and not STATE.exists()
subprocess.run(['node','scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
placements=plan['voicePlacements'];ps08=next(p for p in placements if p['id']=='08-scoring-feedback-part-24')
guide03=next(p for p in placements if p['voiceId']=='12-observe-equal-quantity')
last03=next(p for p in placements if p['id']=='03-same-count-part-07')
old08=read(W/'mixed-asr-v1/context-08-complete-p3.json')
expected08=[c['ko'] for c in cap['chunks'] if c['scene']=='08-scoring-feedback' and c['paragraph'] in [2,3]]
expected03=[c['ko'] for c in cap['chunks'] if c['scene']=='12-observe-equal-quantity' or (c['scene']=='03-same-count' and c['paragraph']==3)]
windows=[dict(label='08-complete-p2-p3-current-mix-beam5',start=ps08['startSample']*2,end=ps08['endSampleExclusive']*2,expectedKo=expected08),
 dict(label='08-complete-p3-current-mix-beam5',start=old08['fromSample'],end=old08['toSample'],expectedKo=old08['expectedKo']),
 dict(label='03-complete-guide12-p3-current-mix-beam5',start=guide03['startSample']*2,end=last03['endSampleExclusive']*2,expectedKo=expected03)]
assert all((x['end']-x['start'])/48000+1.2<30 for x in windows)
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
os.environ['PATH']='C:/ProgramData/HP/LCDDisplayHelper/bin'+os.pathsep+os.environ.get('PATH','')
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
D.mkdir();p=psutil.Process();s=dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),sessionId=None,
 startedAt=now(),resource=a.resource,mixSha256=sha(mix),planSha256=sha(W/'plan.json'),cpuThreads=2,gpu=0,
 status='loading-three-current-mixed-resolution-contexts',total=3,completed=0,exitCode=None,automaticApproval=False,
 expectedWasRecognizerPrompt=False,whole31Rerun=False,newTts=0,researchControlChanges=0)
save(STATE,s)
save(D/'request.json',dict(windows=windows,paddingSamplesEachSide=28800,decoding='beam5,no chunking; all windows below30sec',
 expectedWasRecognizerPrompt=False,mixSha256=s['mixSha256'],automaticApproval=False))
try:
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1);mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,
  attn_implementation='eager',local_files_only=True).to('cpu');processor=AutoProcessor.from_pretrained(str(mp),local_files_only=True)
 tr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
 for x in windows:
  with wave.open(str(mix),'rb')as w:
   params=w.getparams();assert (params.framerate,params.nchannels,params.sampwidth)==(48000,2,2)
   w.setpos(x['start']);pcm=w.readframes(x['end']-x['start'])
  padded=bytes(28800*4)+pcm+bytes(28800*4);path=D/(x['label']+'.wav')
  with wave.open(str(path),'wb')as w:w.setparams(params);w.writeframes(padded)
  with wave.open(str(path),'rb')as w:assert w.readframes(w.getnframes())==padded
  s.update(status='transcribing-'+x['label'],activeWindow=x['label'],observedAt=now());save(STATE,s)
  raw=tr(str(path),generate_kwargs={'language':'korean','task':'transcribe','num_beams':5},return_timestamps='word')
  row={**x,'text':raw['text'],'words':raw['chunks'],'windowPath':path.relative_to(ROOT).as_posix(),'windowSha256':sha(path),
   'exactCurrentMixPcmBytesMatched':True,'mixPcmSliceSha256':hashlib.sha256(pcm).hexdigest(),
   'expectedWasRecognizerPrompt':False,'directlyCompared':False,'automaticApproval':False}
  save(D/(x['label']+'.json'),row);s['completed']+=1;save(STATE,s)
  print(json.dumps(dict(label=x['label'],text=row['text']),ensure_ascii=False),flush=True)
 assert sha(mix)==s['mixSha256'] and sha(W/'plan.json')==s['planSha256']
 s.update(status='closed-current-mixed-resolution-await-direct-review',exitCode=0,endedAt=now());save(STATE,s)
except BaseException:
 import traceback
 s.update(status='closed-current-mixed-resolution-failed',exitCode=1,endedAt=now(),error=traceback.format_exc());save(STATE,s);raise
