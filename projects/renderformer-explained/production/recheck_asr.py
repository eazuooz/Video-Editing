"""Independent short-window retranscription. Never trim audio based on ASR alone."""
from pathlib import Path
import json
import numpy as np
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'shared/output/narration/renderformer-explained/qwen3-1.7b-balanced-v1'
OUT=ROOT/'projects/renderformer-explained/production/body-review/asr-recheck'
OUT.mkdir(exist_ok=True)
torch.set_num_threads(4)
name='openai/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(name,dtype=torch.float16,low_cpu_mem_usage=True,attn_implementation='eager').to('cuda')
processor=AutoProcessor.from_pretrained(name)
transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,
 feature_extractor=processor.feature_extractor,device=0,dtype=torch.float16)
requests=[('06',0,30),('14',-9,None),('19',8,19),('22',0,8),('66',6,21)]
results=[]
for sid,start,end in requests:
    samples,sr=sf.read(BASE/f'chunks/{sid}-scene.wav',dtype='float32')
    duration=len(samples)/sr
    start=max(0,duration+start) if start<0 else start
    end=min(duration,end) if end is not None else duration
    part=samples[round(start*sr):round(end*sr)]
    if part.ndim>1:part=part.mean(axis=1)
    target=OUT/f'page{sid}-window.wav';sf.write(target,part,sr)
    result=transcriber(str(target),generate_kwargs={'language':'korean','task':'transcribe','num_beams':5},return_timestamps=True)
    record={'page':int(sid),'start':start,'end':end,'result':result,'humanListeningApproved':False}
    results.append(record);print(json.dumps(record,ensure_ascii=False),flush=True)
    (OUT/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
