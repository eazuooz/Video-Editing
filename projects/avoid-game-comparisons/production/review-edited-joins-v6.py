"""New whole/context CPU readbacks of edited10/12/13; no TTS or GPU use."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,time,traceback
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'measured-edit-v6'
STATE=WORK/'edited-join-asr-execution.json';DEST=WORK/'edited-join-asr-local'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,d):
 temp=p.with_name(p.name+f'.{os.getpid()}.writing')
 for attempt in range(30):
  try:temp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(temp,p);return
  except OSError:
   if attempt==29:raise
   time.sleep(.1)
assert not STATE.exists() and not DEST.exists();DEST.mkdir()
request=read(WORK/'edited-join-asr-request.json')
for r in request['protectedInputs']:assert sha(ROOT/r['path'])==r['sha256']
state=dict(startedAt=now(),pid=os.getpid(),sessionId=None,status='loading-local-CPU-whisper',device='cpu',threads=2,cpuProductionJobs=1,gpuJobs=0,activeTasks=[],results=[],exitCode=None,readbackComplete=False,directReview=False,finalMixAsrApproved=False,humanWholeListening='pending')
def checkpoint():
 write(STATE,state)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='avoid-game-comparisons')
 item.update(stage='current15-edited-quiet-joins-CPU-ASR',updatedAt=now(),nextAction='Directly compare new whole10/12/13 and independent quiet-join readbacks, then finish final cue/diagram/native pixels. Every current PCM is preserved; final video is incomplete.')
 item['execution'].update(observedAt=now(),phase=item['stage'],status=state['status'],pid=os.getpid(),sessionId=state['sessionId'],alive=bool(state['cpuProductionJobs']),cpuProductionJobs=state['cpuProductionJobs'],gpuSynthesisJobs=0,renderJobs=0,uploads=0,state=STATE.relative_to(ROOT).as_posix(),activeTasks=[dict(kind='edited-join-CPU-ASR',pid=os.getpid())] if state['cpuProductionJobs'] else [])
 q['updatedAt']=now();write(qp,q)
 for p in [BASE/'latest-checkpoint.json',ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/latest-checkpoint.json']:
  d=read(p)
  for key in ['stage','execution','updatedAt','nextAction']:d[key]=item[key]
  write(p,d)
checkpoint()
try:
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
 processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
 transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
 for c in request['contexts']:
  p=ROOT/c['audioPath'];assert sha(p)==c['audioSha256'];audio,sr=sf.read(p,dtype='float32',always_2d=True)
  a=round(c['fromSeconds']*sr);z=min(len(audio),round(c['toSeconds']*sr));wav=DEST/(c['id']+'.wav');sf.write(wav,audio[a:z],sr,subtype='PCM_16')
  state.update(status='transcribing-'+c['id']);checkpoint();print('Transcribing '+c['id'],flush=True)
  raw=transcriber(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
  result={**c,'actualFromSeconds':a/sr,'actualToSeconds':z/sr,'text':raw['text'],'words':raw['chunks'],'expectedWasRecognizerPrompt':False,'directReview':False}
  write(DEST/(c['id']+'.json'),result);state['results'].append(result);checkpoint();print(raw['text'],flush=True)
 for r in request['protectedInputs']:assert sha(ROOT/r['path'])==r['sha256']
 state.update(status='closed-edited-join-ASR-awaiting-direct-whole-review',cpuProductionJobs=0,endedAt=now(),exitCode=0,readbackComplete=True);checkpoint()
except BaseException:
 state.update(status='closed-edited-join-ASR-failed',cpuProductionJobs=0,endedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();raise
