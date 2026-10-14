"""Read ambiguous pronunciation in complete paired contexts, without prompts."""
import pathlib,json,hashlib,datetime
import numpy as np,soundfile as sf,torch
from scipy.signal import resample_poly
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
R=pathlib.Path(__file__).resolve().parents[4];A=R/'shared/output/narration/game-lighting-history-01/continuity-v2';O=R/'projects/game-lighting-history-01/production/local/continuity-v2/context-asr';O.mkdir(parents=True,exist_ok=True)
torch.set_num_threads(2)
snapshots=pathlib.Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots');modelpath=next(p for p in snapshots.iterdir() if (p/'model.safetensors').exists())
model=AutoModelForSpeechSeq2Seq.from_pretrained(modelpath,torch_dtype=torch.float32,attn_implementation='eager',use_safetensors=True,low_cpu_mem_usage=True)
proc=AutoProcessor.from_pretrained(modelpath);asr=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,device='cpu')
for i in range(0,12,2):
 out=O/f'pair-{i//2+1:02}.json'
 if out.exists():continue
 parts=[];hashes=[]
 for num in [i+1,i+2]:
  p=A/'chunks'/f'c{num:02}-scene.wav';data,sr=sf.read(p,dtype='float32');assert sr==24000
  parts.extend([data,np.zeros(9600,dtype='float32')]);hashes.append(dict(id=f'c{num:02}',sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 audio=resample_poly(np.concatenate(parts),2,3)
 result=asr(dict(raw=audio,sampling_rate=16000),generate_kwargs=dict(language='korean',task='transcribe'),return_timestamps='word')
 result.update(sourceHashes=hashes,method='Independent complete paired context; no expected text prompt; CPU two threads.',reviewed=False)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(f'pair-{i//2+1:02} complete',flush=True)
