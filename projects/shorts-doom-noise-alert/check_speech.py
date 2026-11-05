"""Read the actual encoded mix in each authored narration window, without a text prompt."""
import hashlib
import json
import subprocess
import time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
media=Path(json.loads((P/'project.json').read_text(encoding='utf8'))['mediaRoot'])
out=media/'final-reviewed-v1';wav=out/'captioned.mp4'
torch.set_num_threads(3)
model_id=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
if not (model_id/'config.json').exists():model_id='openai/whisper-large-v3-turbo'
proc=AutoProcessor.from_pretrained(model_id,local_files_only=True)
model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,local_files_only=True,dtype=torch.float32).eval()
while not (out/'delivery.json').exists():time.sleep(3)
pcm=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(wav),'-ar','16000','-ac','1','-f','f32le','-']),'<f4')
reports=[]
for row in json.loads((media/'edit/timing.json').read_text(encoding='utf8')):
    s=pcm[round(row['start']*16000):round(row['end']*16000)]
    f=proc(s,sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
    with torch.inference_mode():ids=model.generate(f.input_features,attention_mask=f.attention_mask,language='korean',task='transcribe',max_new_tokens=160)
    raw=proc.batch_decode(ids,skip_special_tokens=True)[0]
    reports.append(dict(section=row['n'],start=row['start'],end=row['end'],text=raw))
    print(row['n'],raw,flush=True)
(out/'asr.json').write_text(json.dumps(dict(masterSha256=hashlib.file_digest(wav.open('rb'),'sha256').hexdigest(),input='encoded captioned AAC mix',expectedTextPromptUsed=False,segments=reports),indent=2,ensure_ascii=False),encoding='utf8')
