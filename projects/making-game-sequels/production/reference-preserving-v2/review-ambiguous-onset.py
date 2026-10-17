"""Resolve one observed ASR discrepancy with a complete two-sentence context."""
from pathlib import Path
import json,hashlib
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';L=P/'production/local/reference-preserving-v2';N=R/'shared/output/narration/making-game-sequels/reference-preserving-v2'
state=json.loads((L/'voice-review-execution.json').read_text());assert state['status']=='asr-ready-for-direct-full-text-review','Wait for whole recognition to finish; do not overlap heavy jobs'
assert json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'))['selectedVideo']==P.name
source=N/'chunks/08-scene.wav';a,sr=sf.read(source,dtype='float32');out=L/'research/scene08-onset-context.wav';sf.write(out,np.concatenate([np.zeros(round(.3*sr)),a[:round(12.6*sr)],np.zeros(round(.3*sr))]),sr)
cache=L/'research/scene08-onset-context-asr.json';sig=hashlib.sha256(out.read_bytes()).hexdigest()
if cache.exists() and json.loads(cache.read_text(encoding='utf8'))['contextSha256']==sig:raise SystemExit('Current independent context already recognized; reuse it')
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
torch.set_num_threads(8);local=R/'qwen3-tts/models/whisper-large-v3-turbo';modelid=str(local) if (local/'config.json').exists() else 'openai/whisper-large-v3-turbo';m=AutoModelForSpeechSeq2Seq.from_pretrained(modelid,dtype=torch.float32,attn_implementation='eager',local_files_only=True);p=AutoProcessor.from_pretrained(modelid,local_files_only=True)
asr=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float32,device='cpu');r=asr(str(out),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
cache.write_text(json.dumps({'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'contextSha256':sig,'sourceRange':[0,12.6],'silencePaddingEachSide':.3,'reason':'Whole current ASR wrote 이럴 보면 where script says 이렇게 보면; inspect the complete first two sentences independently','text':r['text'],'words':r['chunks'],'noExpectedTextPrompt':True,'humanListening':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(r['text'])
