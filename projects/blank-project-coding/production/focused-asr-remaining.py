"""Independent short-window recognition with silence context; no expected-text prompt."""
from pathlib import Path
import json,hashlib
import soundfile as sf,numpy as np,torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3];WORK=Path(__file__).parent;out=ROOT/'shared/output/narration/blank-project-coding/qwen3-1.7b-balanced-v1'
torch.set_num_threads(2);model_id=str(ROOT/'qwen3-tts/models/whisper-large-v3-turbo');model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cuda:0');processor=AutoProcessor.from_pretrained(model_id)
asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0');results=[]
for sid,a,b in [('09',3,11),('12',0,11),('16',0,11),('25',0,12)]:
 source=out/'chunks'/f'{sid}-scene.wav';data,rate=sf.read(source);tmp=WORK/f'focused-{sid}-context.wav';sf.write(tmp,np.concatenate([np.zeros(rate),data[round(a*rate):round(b*rate)],np.zeros(rate)]),rate)
 r=asr(str(tmp),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word');result={'scene':sid,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'in':a,'out':b,'silenceContextSeconds':1,'text':r['text'],'words':r['chunks'],'method':'Independent short-window recognition without expected-text prompt','humanListening':'pending'};results.append(result)
 (WORK/'focused-asr-remaining.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(sid,r['text'],flush=True)
