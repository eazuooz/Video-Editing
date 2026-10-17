"""Only observed final ASR ambiguities, complete contexts and no expected-text prompt."""
from pathlib import Path
import json,hashlib,psutil
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[4]; P=R/'projects/making-game-sequels'; O=P/'production/local/reference-preserving-v2/edit'
assert json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'))['selectedVideo']==P.name
source=O/'encoded-audio.wav'; cache=O/'final-contexts-asr.json'; sig=hashlib.sha256(source.read_bytes()).hexdigest()
if cache.exists() and json.loads(cache.read_text(encoding='utf8'))['sourceSha256']==sig: raise SystemExit('Reuse completed current contexts')
me=psutil.Process(); family={p.pid for p in [me,*me.parents()]}; assert not [p.pid for p in psutil.process_iter(['name']) if p.pid not in family and (p.info['name'] or '').lower().startswith('python')]
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
torch.set_num_threads(8); local=R/'qwen3-tts/models/whisper-large-v3-turbo'; mid=str(local) if (local/'config.json').exists() else 'openai/whisper-large-v3-turbo'; m=AutoModelForSpeechSeq2Seq.from_pretrained(mid,dtype=torch.float32,attn_implementation='eager',local_files_only=True); p=AutoProcessor.from_pretrained(mid,local_files_only=True)
asr=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float32,device='cpu'); a,sr=sf.read(source,dtype='float32'); results=[]
for label,start,end in [('experience',272.15,280.95),('oatchi',296.85,313.1),('value-onset',320.95,333.7)]:
 f=O/f'final-context-{label}.wav'; sf.write(f,np.concatenate([np.zeros(round(.3*sr)),a[round(start*sr):round(end*sr)],np.zeros(round(.3*sr))]),sr)
 r=asr(str(f),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word'); results.append({'id':label,'sourceRange':[start,end],'contextSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'text':r['text'],'words':r['chunks']}); print(label,r['text'],flush=True)
cache.write_text(json.dumps({'sourceSha256':sig,'noExpectedTextPrompt':True,'wholeFinalAsrRepeated':False,'contexts':results,'humanListening':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
