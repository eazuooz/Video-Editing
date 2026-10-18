"""Independent complete introductory contexts only, to resolve flagged source ASR."""
import os
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
from pathlib import Path
import torch,json
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local'
torch.set_num_threads(3);m='openai/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(m,dtype=torch.float32,attn_implementation='eager',local_files_only=True).to('cpu');processor=AutoProcessor.from_pretrained(m,local_files_only=True)
asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,device='cpu')
import soundfile as sf
import scipy.signal
results=[]
for version in ['v1','v2']:
 f=L/f'intro-context-{version}.wav';a,sr=sf.read(f);a=scipy.signal.resample_poly(a,16000,sr)
 r=asr({'array':a,'sampling_rate':16000},generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word');results.append(dict(version=version,rangeSeconds=[0,len(a)/16000],**r));print(version,r['text'],flush=True)
(L/'intro-independent-asr.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
