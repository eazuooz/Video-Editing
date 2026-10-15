"""Read ambiguous pronunciation in complete paired contexts, without prompts."""
import pathlib,json,hashlib,datetime
import numpy as np,soundfile as sf,torch
from scipy.signal import resample_poly
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
R=pathlib.Path(__file__).resolve().parents[4];A=R/'shared/output/narration/game-lighting-history-01/review-v3';O=R/'projects/game-lighting-history-01/production/local/review-v3/context-asr';O.mkdir(parents=True,exist_ok=True)
torch.set_num_threads(2)
snapshots=pathlib.Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots');modelpath=next(p for p in snapshots.iterdir() if (p/'model.safetensors').exists())
model=AutoModelForSpeechSeq2Seq.from_pretrained(modelpath,torch_dtype=torch.float32,attn_implementation='eager',use_safetensors=True,low_cpu_mem_usage=True)
proc=AutoProcessor.from_pretrained(modelpath);asr=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,device='cpu')
for key,lo,hi in [('v02',10.5,15.2),('v03',17.6,22.4),('v05',16.3,23.76),('v06',0,7.4)]:
 out=O/(key+'.json')
 if out.exists():continue
 p=A/'chunks'/(key+'-scene.wav');data,sr=sf.read(p,dtype='float32');assert sr==24000
 audio=resample_poly(data[round(lo*sr):round(hi*sr)],2,3)
 result=asr(dict(raw=audio,sampling_rate=16000),generate_kwargs=dict(language='korean',task='transcribe'),return_timestamps='word')
 result.update(sourceSha256=hashlib.sha256(p.read_bytes()).hexdigest(),sourceSeconds=[lo,hi],method='Independent complete sentence, no expected prompt, CPU float32 eager',reviewed=False)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(key,result['text'],flush=True)
