"""Independent complete contexts for actual new ambiguities, without text prompts."""
import pathlib,json,hashlib
import numpy as np,soundfile as sf,torch
from scipy.signal import resample_poly
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
R=pathlib.Path(__file__).resolve().parents[4];O=R/'projects/game-lighting-history-01/production/local/review-v3';D=O/'mix-contexts';D.mkdir(exist_ok=True)
rd=lambda p:json.loads(p.read_text(encoding='utf8'))
plan=rd(O/'plan.json');mix=rd(O/'mix-execution.json');selection=['08-r1','08-r8']
for ch in ['07','09a']:
 r=rd(O/'mixed-asr'/(ch+'.json'));selection.append(r['orderedKeys'][-1])
torch.set_num_threads(2)
modelpath=next(p for p in pathlib.Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots').iterdir() if (p/'model.safetensors').exists())
model=AutoModelForSpeechSeq2Seq.from_pretrained(modelpath,torch_dtype=torch.float32,attn_implementation='eager',use_safetensors=True,low_cpu_mem_usage=True,local_files_only=True)
proc=AutoProcessor.from_pretrained(modelpath,local_files_only=True);asr=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,device='cpu')
with sf.SoundFile(O/mix['currentAsrWav']) as f:
 for key in selection:
  p=D/(key+'.json')
  if p.exists():continue
  vs=[v for v in plan['voice'] if v['key']==key];lo=min(v['startFrame']*800 for v in vs);hi=max(v['startFrame']*800+v['samples']*2 for v in vs)
  f.seek(lo);a=f.read(hi-lo,dtype='float32').mean(axis=1);a=resample_poly(a,1,3)
  result=asr(dict(raw=a,sampling_rate=16000),generate_kwargs=dict(language='korean',task='transcribe'),return_timestamps='word')
  result.update(key=key,seconds=[lo/48000,hi/48000],decodedAacSha256=mix['outputs'][mix['currentAsrWav']],method='Complete utterance in decoded AAC; independent CPU float32 eager; no expected-text prompt',reviewed=False)
  p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(key,result['text'],flush=True)
