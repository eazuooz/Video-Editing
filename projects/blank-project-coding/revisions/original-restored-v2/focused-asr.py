"""Independent short-window check of ambiguous ASR words; no expected-text prompt."""
from pathlib import Path
import json,hashlib,sys
import soundfile as sf,numpy as np,torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
W=Path(__file__).resolve().parent;R=W.parents[3];out=R/'shared/output/narration/blank-project-coding/original-restored-v2'
torch.set_num_threads(2);model_id=str(R/'qwen3-tts/models/whisper-large-v3-turbo')
model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu');processor=AutoProcessor.from_pretrained(model_id)
asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu');results=[]
windows=[(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]))] if len(sys.argv)==4 else [('10',0,6),('14',0,6)]
output='focused-asr-'+windows[0][0]+'.json' if len(sys.argv)==4 else 'focused-asr.json'
for sid,a,b in windows:
 source=out/'chunks'/f'{sid}-scene.wav';data,rate=sf.read(source);tmp=W/f'focused-{sid}-context.wav';sf.write(tmp,np.concatenate([np.zeros(rate),data[round(a*rate):round(b*rate)],np.zeros(rate)]),rate)
 r=asr(str(tmp),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 results.append({'scene':sid,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'in':a,'out':b,'silenceContextSeconds':1,'text':r['text'],'words':r['chunks'],'method':'Unprompted short-window ASR','humanListening':'pending'})
 (W/output).write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(sid,r['text'],flush=True)
