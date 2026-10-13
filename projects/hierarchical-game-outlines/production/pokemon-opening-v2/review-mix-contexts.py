"""One bounded pass over only unresolved complete passages of the current AAC."""
from pathlib import Path
import os,sys,json,hashlib,datetime,subprocess,psutil
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).resolve().parent;R=P.parents[3];S=P/'mix-contexts-v1.json'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
assert not S.exists()
control=read(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']=='hierarchical-game-outlines' and control['newProductionAuthorization']['fullProductionAuthorized']
prior=read(P/'mix-asr-v1.json');assert prior['exitCode']==0
try:assert abs(psutil.Process(prior['pid']).create_time()-prior['createTime'])>.01
except psutil.NoSuchProcess:pass
request=read(P/'mix-context-plan-v1.json');assert request['mixSha256']==sha(P/'current-mix-v1.m4a')
me=psutil.Process();me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
state=dict(status='running',at=now(),pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd(),resource=dict(cpu=psutil.cpu_percent(interval=1),ram=psutil.virtual_memory().available,gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True)),cpuThreads=2,gpuJobs=0,expectedWasPrompt=False,results=[])
assert state['resource']['cpu']<85 and state['resource']['ram']>8e9
def save():S.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save()
import torch,soundfile as sf
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
torch.set_num_threads(2);torch.set_num_interop_threads(1);m=R/'qwen3-tts/models/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(str(m),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu');processor=AutoProcessor.from_pretrained(str(m),local_files_only=True)
pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
for r in request['contexts']:
 source=P/f'mix-review-local/{r["scene"]}.wav';x,sr=sf.read(source);part=P/f'mix-context-{r["id"]}-local.wav';sf.write(part,x[round(r['start']*sr):round(r['end']*sr)],sr,subtype='PCM_16')
 result=pipe(str(part),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 row=dict(**r,sourceSha256=sha(source),cropSha256=sha(part),actual=result['text'],words=result['chunks']);state['results'].append(row);save();print(json.dumps(row,ensure_ascii=False),flush=True)
state.update(status='complete-awaiting-direct-review',exitCode=0,endedAt=now(),humanListening=False);save()
