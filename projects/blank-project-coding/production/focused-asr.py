"""Independent short-window recognition for a technical term; no expected-text prompt."""
from pathlib import Path
import json,hashlib
import soundfile as sf,torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3];WORK=Path(__file__).parent;out=ROOT/'shared/output/narration/blank-project-coding/qwen3-1.7b-balanced-v1'
source=out/'chunks/20-scene.wav';data,rate=sf.read(source);tmp=WORK/'focused-20.wav';sf.write(tmp,data[round(11.5*rate):round(19*rate)],rate)
torch.set_num_threads(2);model_id=str(ROOT/'qwen3-tts/models/whisper-large-v3-turbo');model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cuda:0');processor=AutoProcessor.from_pretrained(model_id)
asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0')
r=asr(str(tmp),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word');result={'scene':'20','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'in':11.5,'out':19,'text':r['text'],'words':r['chunks'],'method':'Independent short-window recognition without expected-text prompt','humanListening':'pending'}
(WORK/'focused-asr-20.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
