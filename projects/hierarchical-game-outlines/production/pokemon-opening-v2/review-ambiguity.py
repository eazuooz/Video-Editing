from pathlib import Path
import os,sys,json,datetime,hashlib,subprocess
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
sys.stdout.reconfigure(encoding='utf-8')
import psutil,soundfile as sf
P=Path(__file__).resolve().parent;R=P.parents[3];S=P/'voice-ambiguity.json';assert not S.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=read(P/'voice-asr-v1.json');assert prior['exitCode']==0
try:assert abs(psutil.Process(prior['pid']).create_time()-prior['createTime'])>.01
except psutil.NoSuchProcess:pass
control=read(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']=='hierarchical-game-outlines'
p=psutil.Process();state=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='running',pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),resource=dict(cpu=psutil.cpu_percent(interval=1),ram=psutil.virtual_memory().available,gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True)),cpuThreads=2,gpuJobs=0,expectedWasPrompt=False)
assert state['resource']['cpu']<85 and state['resource']['ram']>8e9
def save():S.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save();src=P/'generated-narration/chunks/08p01-scene.wav';x,sr=sf.read(src);part=P/'08p01-second-sentence-local.wav';sf.write(part,x[round(3.08*sr):],sr,subtype='PCM_16')
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
torch.set_num_threads(2);torch.set_num_interop_threads(1);m=R/'qwen3-tts/models/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(str(m),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu');processor=AutoProcessor.from_pretrained(str(m),local_files_only=True)
pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
res=pipe(str(part),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
state.update(status='complete-awaiting-direct-review',exitCode=0,sourceSha256=sha(src),contextStart=3.08,contextEnd=len(x)/sr,expected='영상 주제와 세부 설명을 묶거나, 공부할 내용과 질문을 정리할 때도 사용할 수 있습니다.',actual=res['text'],words=res['chunks'],humanListening=False);save();print(json.dumps(state,ensure_ascii=False))
