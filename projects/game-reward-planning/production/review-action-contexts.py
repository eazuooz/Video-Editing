"""Independent CPU ASR of changed title/particle and final-phrase contexts."""
import hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/narration/game-reward-planning/qwen3-1.7b-balanced-v1'
WORK=BASE/'action-context-asr-v1';WORK.mkdir(exist_ok=False)
now=lambda:datetime.now(timezone.utc).isoformat()
state={'pid':os.getpid(),'startedAt':now(),'status':'running','device':'cpu','threads':2,'completed':[],'evidenceOnly':True,'humanListening':'pending'}
def save():
 state['updatedAt']=now();(WORK/'execution.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save();torch.set_num_threads(2)
model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu')
processor=AutoProcessor.from_pretrained(str(model_path))
transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
contexts=[('02-title','02',0,5),('08-opening','08',0,8.3),('08-title','08',8.3,18.5),('10-floor','10',0,9),('12-new-ammo','12',0,13),('12-windup','12',25,36),('04-ending','04',31,38.64),('12-ending','12',47,54.48)]
records=[]
for name,scene,a,z in contexts:
 file=OUT/'chunks'/f'{scene}-scene.wav';samples,rate=sf.read(file,dtype='float32')
 crop=WORK/(name+'.wav');sf.write(crop,samples[round(a*rate):round(z*rate)],rate,subtype='PCM_16')
 raw=transcriber(str(crop),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 result={'id':name,'scene':scene,'sourceInSeconds':a,'sourceOutSeconds':z,'sourceSha256':hashlib.sha256(file.read_bytes()).hexdigest(),'text':raw['text'],'words':raw['chunks'],'directReview':'pending'}
 records.append(result);(WORK/(name+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 state['completed'].append(name);save();print(name+': '+raw['text'],flush=True)
(WORK/'index.json').write_text(json.dumps({'records':records,'evidenceOnly':True,'humanListening':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
state.update(status='finished-awaiting-direct-context-review',endedAt=now(),exitCode=0);save()
