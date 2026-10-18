"""Recognize only four ambiguous complete contexts; no expected-text prompt."""
from pathlib import Path
import hashlib,json
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
from audio_pipeline import require_authorized

R=Path(__file__).resolve().parents[4]
O=R/'shared/output/narration/player-customization/reference-preserving-v2'
raw=O/'narration-source.wav'
out=O/'ambiguous-context-asr.json'
require_authorized('four-ambiguous-contexts-only')
if out.exists():
    print('Existing isolated context results retained; no new recognition')
    raise SystemExit(0)
torch.set_num_threads(4)
M=R/'qwen3-tts/models/whisper-large-v3-turbo'
model_id=str(M) if (M/'config.json').exists() else 'openai/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=torch.float32,attn_implementation='eager',local_files_only=True)
processor=AutoProcessor.from_pretrained(model_id,local_files_only=True)
recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
audio,rate=sf.read(raw,dtype='float32')
ranges=[('fictional-weapon-paragraph',111.15,127.15),('icons-paragraph',163.3,178.7),('starting-combination-paragraph',207.2,216.7),('manual-adjustment-paragraph',248.1,260.7)]
rows=[]
for name,start,end in ranges:
    result=recognize({'raw':audio[round(start*rate):round(end*rate)],'sampling_rate':rate},generate_kwargs={'language':'korean','task':'transcribe','num_beams':1})
    rows.append(dict(id=name,sourceStart=start,sourceEnd=end,recognized=result['text'],expectedPrompt=None))
    print(name,result['text'],flush=True)
out.write_text(json.dumps(dict(sourceSha256=hashlib.sha256(raw.read_bytes()).hexdigest(),scope='Four ambiguous complete paragraphs only; not a repeat full narration ASR',cpuThreads=4,foreignJobsChanged=False,contexts=rows,humanListening='pending'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
