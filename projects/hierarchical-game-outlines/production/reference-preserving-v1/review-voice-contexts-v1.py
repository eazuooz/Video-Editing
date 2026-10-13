"""Resolve two specific whole-ASR alternatives without rerunning TTS or whole ASR."""
from pathlib import Path
import os,json,hashlib,datetime,traceback,subprocess
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']: os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
import psutil,soundfile as sf
P=Path(__file__).resolve().parent; ROOT=P.parents[3]
STATE=P/'voice-contexts-v1.json'
assert not STATE.exists(),'Inspect existing execution; no repeated request'
whole=json.loads((P/'voice-asr-v1.json').read_text(encoding='utf-8'))
assert whole['exitCode']==0
try: assert abs(psutil.Process(whole['pid']).create_time()-whole['createTime'])>.01
except psutil.NoSuchProcess: pass
me=psutil.Process();me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=dict(status='running',pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd(),startedAt=now(),cpuThreads=2,gpuJobs=0,wholeSha256=sha(P/'voice-asr-v1.json'),results=[],exitCode=None)
state['resource']=dict(cpu=psutil.cpu_percent(interval=1),availableMemoryBytes=psutil.virtual_memory().available,gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True).stdout)
assert state['resource']['cpu']<85 and state['resource']['availableMemoryBytes']>8_000_000_000
def save():STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save()
try:
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1)
 modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
 m=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
 pr=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
 asr=pipeline('automatic-speech-recognition',model=m,tokenizer=pr.tokenizer,feature_extractor=pr.feature_extractor,dtype=torch.float32,device='cpu')
 script=json.loads((P/'narration.ko.json').read_text(encoding='utf-8'))['scenes']
 for sid,a,b,lineids in [('05',14.24,31.44,[1,2]),('06',0,9.64,[0])]:
  src=P/f'narration/chunks/{sid}-scene.wav';x,sr=sf.read(src,dtype='float32');crop=x[round(a*sr):round(b*sr)]
  dest=P/f'narration/{sid}-independent-context-v1.wav';sf.write(dest,crop,sr,subtype='PCM_16')
  result=asr(str(dest),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
  scene=next(s for s in script if s['id']==sid)
  row=dict(id=sid,sourceSha256=sha(src),start=a,end=b,expected=' '.join(scene['lines'][i] for i in lineids),actual=result['text'],words=result['chunks'],contextSha256=sha(dest),expectedWasPrompt=False,directReview=False)
  state['results'].append(row);save();print(json.dumps(row,ensure_ascii=False),flush=True)
 state.update(status='complete-awaiting-direct-review',exitCode=0,finishedAt=now(),humanListening=False);save()
except BaseException:
 state.update(status='failed',exitCode=1,error=traceback.format_exc(),finishedAt=now());save();raise
