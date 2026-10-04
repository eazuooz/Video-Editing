import hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
import soundfile as sf,torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/narration/game-reward-planning/qwen3-1.7b-balanced-v1-phrase-repair1'
WORK=BASE/'repair1/candidate-context';WORK.mkdir(exist_ok=False)
torch.set_num_threads(2);model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
state={'pid':os.getpid(),'startedAt':datetime.now(timezone.utc).isoformat(),'device':'cpu','status':'running','completed':[]}
def save(): (WORK/'execution.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
save();model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu')
p=AutoProcessor.from_pretrained(str(model_path));asr=pipeline('automatic-speech-recognition',model=model,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float32,device='cpu')
rows=[]
for name,sid,a,z in [('02a-start','02a',0,3.3),('02a-action','02a',3.3,8.16)]:
 file=OUT/'chunks'/(sid+'-scene.wav');x,rate=sf.read(file,dtype='float32');crop=WORK/(name+'.wav');sf.write(crop,x[round(a*rate):round(z*rate)],rate,subtype='PCM_16')
 result=asr(str(crop),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 rows.append({'id':name,'source':file.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.sha256(file.read_bytes()).hexdigest(),'from':a,'to':z,**result});state['completed'].append(name);save();print(name+':'+result['text'],flush=True)
(WORK/'asr.json').write_text(json.dumps({'rows':rows,'directReview':'pending','humanListening':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
state.update(status='finished-awaiting-direct-review',endedAt=datetime.now(timezone.utc).isoformat(),exitCode=0);save()
