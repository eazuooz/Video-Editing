"""Bounded context recheck of ambiguous ASR numerals; original PCM untouched."""
from pathlib import Path
from datetime import datetime,timezone
import importlib.util,json,os,subprocess,time,uuid
import psutil
P=Path(__file__).resolve().parents[1];R=P.parents[1];A=P/'production/local/audio-v1';W=A/'review/targeted-context';W.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
s=importlib.util.spec_from_file_location('g',R/'projects/game-math-shading-lights/production/run-capture-queue.py');G=importlib.util.module_from_spec(s);s.loader.exec_module(G)
statefile=W/'worker.json';lease=R/'shared/output/GPU_HANDOFF.json'
if statefile.exists():
 old=read(statefile)
 try:assert abs(psutil.Process(old['pid']).create_time()-old['createTime'])>.1,'Existing review active'
 except psutil.NoSuchProcess:pass
 assert old['status']!='evidence-ready','Preserve complete evidence'
state=dict(pid=os.getpid(),createTime=psutil.Process().create_time(),status='waiting',humanListening=False,automation=False,startedAt=now());owned=None;deadline=time.monotonic()+12*3600
try:
 while owned is None:
  G.authorized();reason=G.idle_reason();state.update(reason=reason,checkedAt=now());save(statefile,state)
  if reason is None:
   candidate=str(uuid.uuid4())
   try:
    with lease.open('x',encoding='utf-8') as f:json.dump(dict(owner=P.name+'-targeted-asr',id=candidate,pid=os.getpid(),createdAt=now()),f)
   except FileExistsError:pass
   else:owned=candidate;break
  if time.monotonic()>deadline:raise RuntimeError('Bounded wait ended')
  time.sleep(15)
 state.update(status='transcribing');save(statefile,state)
 os.environ.update(OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
 import torch,numpy as np,soundfile as sf
 from scipy.signal import resample_poly
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1);free,total=torch.cuda.mem_get_info();assert free>=9*1024**3;torch.cuda.set_per_process_memory_fraction(7*1024**3/total)
 modelpath='C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots/41f01f3fe87f28c78e2fbf8b568835947dd65ed9'
 model=AutoModelForSpeechSeq2Seq.from_pretrained(modelpath,dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cuda').eval();processor=AutoProcessor.from_pretrained(modelpath)
 pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device=0)
 pcm,sr=sf.read(A/'narration.wav',dtype='float32');entries={e['scene_id']:e for e in read(A/'narration.timing.json')['entries']};results=[]
 for sid,begin,end,label in [('020',3.56,7.5,'subtract-one'),('020',12.0,17.65,'normal-three-components'),('025',8.3,19.6,'q-s-t-index-two'),('027',9.0,18.6,'tangent-bitangent-q2')]:
  e=entries[sid];x=pcm[round((e['start']+begin)*sr):round((e['start']+end)*sr)];from math import gcd
  g=gcd(sr,16000)
  with torch.inference_mode():r=pipe({'array':resample_poly(x,16000//g,sr//g).astype(np.float32),'sampling_rate':16000},generate_kwargs={'language':'korean','task':'transcribe','num_beams':5},return_timestamps=True)
  results.append(dict(scene=sid,begin=begin,end=end,label=label,text=r['text'],chunks=r.get('chunks',[]),originalPcmSha256=G.sha(A/'narration.wav'),method='Complete phrase context, no script prompt, five-beam decoder; not perceptual listening'))
  save(W/'results.json',dict(results=results,humanListening=False));print(sid,label,r['text'],flush=True)
 state.update(status='evidence-ready',finishedAt=now());save(statefile,state)
except BaseException as exc:state.update(status='failed-or-blocked',error=repr(exc));save(statefile,state);raise
finally:G.release_lease(owned)
