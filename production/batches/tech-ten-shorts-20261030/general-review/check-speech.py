"""Check new spoken takes independently and retain raw recognition for human review."""
import hashlib
import json
import subprocess
import time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoProcessor,AutoModelForSpeechSeq2Seq

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
media=Path(json.loads((HERE.parent/'batch.json').read_text(encoding='utf8'))['mediaRoot'])
work=media/'general-review'
modeldir=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
modelid=str(modeldir) if (modeldir/'config.json').exists() else 'openai/whisper-large-v3-turbo'
torch.set_num_threads(3)
processor=AutoProcessor.from_pretrained(modelid,local_files_only=True)
asr=AutoModelForSpeechSeq2Seq.from_pretrained(modelid,local_files_only=True,dtype=torch.float32).eval()
for n in [5,10]:
    pin=work/f'{n:02}'/'voice-files.json'
    while not pin.exists():time.sleep(3)
    reports=[]
    for record in json.loads(pin.read_text(encoding='utf8')).values():
        path=Path(record['path'])
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest!=record['sha256']:raise RuntimeError('Voice changed after edit selection')
        raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-ar','16000','-ac','1','-f','f32le','-'])
        features=processor(np.frombuffer(raw,'<f4'),sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
        with torch.inference_mode():
            ids=asr.generate(features.input_features,attention_mask=features.attention_mask,
                             language='korean',task='transcribe',max_new_tokens=160)
        transcript=processor.batch_decode(ids,skip_special_tokens=True)[0]
        print(n,path.stem,transcript,flush=True)
        reports.append(dict(take=path.name,sha256=digest,rawRecognition=transcript))
    (pin.parent/'speech-check.json').write_text(json.dumps(reports,indent=2,ensure_ascii=False),encoding='utf8')
