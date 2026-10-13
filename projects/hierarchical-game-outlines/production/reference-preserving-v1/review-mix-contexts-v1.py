"""One bounded batch for ambiguous words in the selected final AAC; never a second whole ASR."""
from pathlib import Path
import os,json,hashlib,datetime,subprocess,traceback
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']: os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
import psutil,soundfile as sf
P=Path(__file__).resolve().parent;ROOT=P.parents[3];STATE=P/'mix-contexts-v1.json'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
assert not STATE.exists(),'Reuse actual request, do not repeat'
c=read(ROOT/'shared/publishing/video-production-control.json')
assert c['selectedVideo']=='hierarchical-game-outlines' and c['newProductionAuthorization']['fullProductionAuthorized']
whole=read(P/'mix-asr-v1.json');assert whole['exitCode']==0
try: assert abs(psutil.Process(whole['pid']).create_time()-whole['createTime'])>.01
except psutil.NoSuchProcess: pass
inputs=read(P/'mix-final-inputs-v1.json');assert sha(ROOT/inputs['audio'])==inputs['sha256']
me=psutil.Process();me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
state=dict(status='running',pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd(),startedAt=now(),cpuThreads=2,gpuJobs=0,wholeSha256=sha(P/'mix-asr-v1.json'),audioSha256=inputs['sha256'],results=[],exitCode=None)
state['resource']=dict(cpu=psutil.cpu_percent(interval=1),availableMemoryBytes=psutil.virtual_memory().available,gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True).stdout)
assert state['resource']['cpu']<85 and state['resource']['availableMemoryBytes']>8_000_000_000
def save():STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save()
contexts=[
 ('02-opening','02',0,6.0,'아웃라인은 큰 항목 아래에 작은 항목을 넣어, 글의 포함 관계를 드러내는 방식입니다.'),
 ('02-game','02',11.4,20.5,'사쿠라이가 든 게임은 슈퍼 스매시브라더스 얼티밋입니다. 화면의 큰 메뉴를 고르면 그 안의 선택지가 나타납니다.'),
 ('06-word','06',0,9.64,'이 기능을 써 보기 위해 특별한 기획 도구부터 만들 필요는 없습니다. 데스크톱 워드에서는 보기 탭의 개요 보기에서 문서의 단계를 다룰 수 있습니다.'),
 ('07-conclusion','07',21.7,33.216667,'같은 기술 설명이라도 작업 중에는 입력과 결과를 따로 비교하고, 전달할 때는 제목과 설명을 읽는 순서대로 다듬습니다. 구조를 잡는 도구와 완성된 문서의 표현은 같을 필요가 없습니다.')]
try:
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1)
 modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
 m=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
 pr=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
 asr=pipeline('automatic-speech-recognition',model=m,tokenizer=pr.tokenizer,feature_extractor=pr.feature_extractor,dtype=torch.float32,device='cpu')
 for key,sid,a,b,expected in contexts:
  item=next(x for x in inputs['scenes'] if x['id']==sid);src=ROOT/item['path'];assert sha(src)==item['sha256']
  x,sr=sf.read(src,dtype='float32');crop=x[round(a*sr):round(b*sr)];dest=P/f'mix-review-v2-local/{key}-context.wav';sf.write(dest,crop,sr,subtype='PCM_16')
  result=asr(str(dest),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
  row=dict(id=key,scene=sid,sourceSha256=item['sha256'],start=a,end=b,expected=expected,actual=result['text'],words=result['chunks'],contextSha256=sha(dest),expectedWasPrompt=False,directReview=False)
  state['results'].append(row);save();print(json.dumps({k:row[k] for k in ['id','expected','actual']},ensure_ascii=False),flush=True)
 state.update(status='complete-awaiting-direct-review',exitCode=0,finishedAt=now(),humanListening=False);save()
except BaseException:
 state.update(status='failed',exitCode=1,error=traceback.format_exc(),finishedAt=now());save();raise
