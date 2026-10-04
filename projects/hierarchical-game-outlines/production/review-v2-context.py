"""Independent current-PCM join/end read-backs; no prompting or automatic approval."""
from pathlib import Path
import hashlib,json,os
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/hierarchical-game-outlines/production/repair1/v2-context'
SOURCE=ROOT/'shared/output/narration/hierarchical-game-outlines/qwen3-1.7b-balanced-v2'
BASE.mkdir(parents=True,exist_ok=True)
if (BASE/'asr.json').exists():raise RuntimeError('Existing v2 context evidence must be reviewed, not repeated.')
requests=[('03',6.0,14.0,'First replacement and retained next paragraph join'),
 ('03',26.0,42.0,'Both joins around fourth paragraph replacement'),
 ('05',6.0,22.0,'Both joins around second paragraph replacement'),
 ('05',33.0,56.184,'Fifth paragraph joins, comparison limitation and complete scene ending'),
 ('05',47.0,56.184,'Independent retained last paragraph; full ASR added a possible hallucinated farewell'),
 ('11',42.0,65.12,'Sixth paragraph joins and final question'),
 ('12',26.0,39.883,'Coaching paragraph join and complete explanation ending')]
print(f'Independent v2-context CPU ASR PID {os.getpid()}',flush=True)
torch.set_num_threads(2)
model_id=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_id),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu')
processor=AutoProcessor.from_pretrained(str(model_id))
transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
results=[]
for i,(sid,start,end,focus) in enumerate(requests,1):
 source=SOURCE/'chunks'/f'{sid}-scene.wav';audio,rate=sf.read(source,dtype='int16')
 cache=json.loads((SOURCE/'asr'/f'{sid}.json').read_text(encoding='utf-8'));digest=hashlib.sha256(source.read_bytes()).hexdigest()
 assert cache['audio_sha256']==digest;end=min(end,len(audio)/rate)
 cut=BASE/f'{i:02d}-{sid}.wav';sf.write(cut,audio[round(start*rate):round(end*rate)],rate,subtype='PCM_16')
 raw=transcriber(str(cut),generate_kwargs={'language':'korean','task':'transcribe','num_beams':5},return_timestamps='word')
 row={'scene':sid,'source':source.relative_to(ROOT).as_posix(),'sourceSha256':digest,'from':start,'to':end,'focus':focus,'text':raw['text'],'words':raw['chunks']};results.append(row)
 (BASE/'asr.json').write_text(json.dumps({'pid':os.getpid(),'device':'cpu','numBeams':5,'complete':len(results)==len(requests),'results':results,'humanListening':'pending','automaticallyApproved':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in row.items() if k!='words'},ensure_ascii=False),flush=True)
