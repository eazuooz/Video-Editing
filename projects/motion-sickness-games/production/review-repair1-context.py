"""Read ambiguous candidate speech in independent contexts; never auto-approve."""
from pathlib import Path
import hashlib,json,os
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/motion-sickness-games/production/repair1/context-review'
SOURCE=ROOT/'shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v1-phrase-repair1'
BASE.mkdir(parents=True,exist_ok=True)
if (BASE/'asr.json').exists():raise RuntimeError('Context evidence already exists; inspect rather than repeat.')
requests=[('03',2.5,7.3,'배경의 나무보다 물줄기가 닿는 표면을 따라가면'),
 ('04a',8.1,9.760041666666666,'조절 값도 따로 둘 수 있죠.'),
 ('04b',6.6,11.44,'한 스위치가 도구를 겨누는 동작과 이동까지 뜻밖에 바꾸지 않게 하세요.'),
 ('05',0,4.5,'이어지는 다른 면에서는 노즐이 기둥과 판자를 따라 움직입니다.'),
 ('05',1.6,4.5,'노즐이 기둥과 판자를 따라 움직입니다.')]
torch.set_num_threads(2)
model_id=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_id),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu')
processor=AutoProcessor.from_pretrained(str(model_id))
transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
results=[]
for i,(sid,start,end,focus) in enumerate(requests,1):
 source=SOURCE/'chunks'/f'{sid}-scene.wav';audio,rate=sf.read(source,dtype='int16')
 cache=json.loads((SOURCE/'asr'/f'{sid}.json').read_text(encoding='utf-8'))
 digest=hashlib.sha256(source.read_bytes()).hexdigest();assert cache['audio_sha256']==digest
 cut=BASE/f'{i:02d}-{sid}.wav';sf.write(cut,audio[round(start*rate):round(end*rate)],rate,subtype='PCM_16')
 raw=transcriber(str(cut),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 row={'scene':sid,'source':source.relative_to(ROOT).as_posix(),'sourceSha256':digest,'from':start,'to':end,'focus':focus,'text':raw['text'],'words':raw['chunks']};results.append(row)
 report={'pid':os.getpid(),'device':'cpu','complete':len(results)==len(requests),'results':results,'humanListening':'pending','automaticallyApproved':False}
 (BASE/'asr.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in row.items() if k!='words'},ensure_ascii=False),flush=True)
