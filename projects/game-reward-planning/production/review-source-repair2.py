"""Independent full/ending read-backs of the single source-word candidate."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,traceback
import soundfile as sf,torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'repair2/asr';WORK.mkdir(exist_ok=False)
FILE=ROOT/'shared/output/narration/game-reward-planning/qwen3-1.7b-balanced-v2-source-repair2/chunks/08b-scene.wav'
now=lambda:datetime.now(timezone.utc).isoformat();state={'pid':os.getpid(),'status':'running','device':'cpu','startedAt':now(),'completed':[],'gpuJobs':0}
def save():(WORK/'execution.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
save()
try:
 torch.set_num_threads(2);mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo';model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu');p=AutoProcessor.from_pretrained(str(mp));asr=pipeline('automatic-speech-recognition',model=model,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float32,device='cpu')
 x,sr=sf.read(FILE,dtype='float32');rows=[]
 for name,a,z in [('full',0,len(x)/sr),('ending',3.1,len(x)/sr)]:
  crop=WORK/(name+'.wav');sf.write(crop,x[round(a*sr):round(z*sr)],sr,subtype='PCM_16');r=asr(str(crop),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word');rows.append({'id':name,'from':a,'to':z,'source':FILE.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.sha256(FILE.read_bytes()).hexdigest(),**r});state['completed'].append(name);save();print(name+': '+r['text'],flush=True)
 (WORK/'asr.json').write_text(json.dumps({'rows':rows,'directReview':'pending','humanWholeListening':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf8');state.update(status='finished-awaiting-direct-review',exitCode=0,endedAt=now());save()
except BaseException:
 state.update(status='failed',exitCode=1,error=traceback.format_exc(),endedAt=now());save();raise
