"""Full changed scene and both preserved-word joins, using CPU ASR."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,traceback
import soundfile as sf,torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'speech-v3';WORK.mkdir(exist_ok=False)
OUT=ROOT/'shared/output/narration/game-reward-planning/qwen3-1.7b-balanced-v3';FILE=OUT/'chunks/08-scene.wav';now=lambda:datetime.now(timezone.utc).isoformat()
state={'pid':os.getpid(),'status':'running','device':'cpu','gpuJobs':0,'startedAt':now(),'completed':[]}
def save():(WORK/'execution.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
save()
try:
 torch.set_num_threads(2);mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo';model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu');p=AutoProcessor.from_pretrained(str(mp));asr=pipeline('automatic-speech-recognition',model=model,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float32,device='cpu');x,sr=sf.read(FILE,dtype='float32');h=hashlib.sha256(FILE.read_bytes()).hexdigest();rows=[]
 for name,a,z in [('full08',0,len(x)/sr),('left-join',7.3,12.5),('right-join',15.8,22.9),('title',0,2.42)]:
  crop=WORK/(name+'.wav');sf.write(crop,x[round(a*sr):round(z*sr)],sr,subtype='PCM_16');r=asr(str(crop),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word');rows.append({'id':name,'scene':'08','from':a,'to':z,'source':FILE.relative_to(ROOT).as_posix(),'sourceSha256':h,**r})
  if name=='full08':(OUT/'asr/08.json').write_text(json.dumps({'scene':'08','audio_sha256':h,'text':r['text'],'words':r['chunks']},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  state['completed'].append(name);save();print(name+': '+r['text'],flush=True)
 (WORK/'contexts.json').write_text(json.dumps({'rows':rows,'directReview':'pending','humanWholeListening':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf8');state.update(status='finished-awaiting-direct-review',exitCode=0,endedAt=now());save()
except BaseException:
 state.update(status='failed',exitCode=1,error=traceback.format_exc(),endedAt=now());save();raise
