"""Independent CPU recognition of a potentially omitted opening, no prompt text.

Preserves the scene cache. A better transcript is evidence only; never inject
the supplied script into words or treat recognition as human listening.
"""
from pathlib import Path
import json,hashlib
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-lines-bounds-teaching-additions-v2';P=ROOT/'projects'/slug
manifest=json.loads((P/'project.json').read_text(encoding='utf8'));out=ROOT/manifest['tts']['outputDir']
wav=out/'chunks/11-01.wav';assert wav.exists()
torch.set_num_threads(2);model_id=str(ROOT/'qwen3-tts/models/whisper-large-v3-turbo')
model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu')
processor=AutoProcessor.from_pretrained(model_id)
transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
raw=transcriber(str(wav),generate_kwargs={'language':'korean','task':'transcribe','num_beams':5},return_timestamps='word')
record={'scene':'11','line':1,'path':wav.relative_to(ROOT).as_posix(),'audioSha256':hashlib.sha256(wav.read_bytes()).hexdigest(),'text':raw['text'],'words':raw['chunks'],'evidence':'independent CPU line-only beam5, no script prompt','originalSceneCachePreserved':True,'humanListeningApproval':False}
(B/'lines-initial-asr-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:record[k] for k in ['text','evidence','humanListeningApproval']},ensure_ascii=False),flush=True)
