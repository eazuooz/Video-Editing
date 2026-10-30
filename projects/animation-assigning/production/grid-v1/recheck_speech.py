"""Focused unprompted recognition; original PCM and whole-source ASR are preserved."""
from pathlib import Path
import os, json, hashlib, sys
H=Path(__file__).resolve().parent
R=H.parents[3]
V=H.parent/'local/grid-v1/voice'
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
sys.path.insert(0,str(H))
import audio_pipeline as ap

def main():
 ap.require_authorized('recognize')
 source=V/'narration-source.wav'
 target=V/'targeted-asr-v1.json'
 if target.exists():
  print('Existing focused review preserved');return
 # Different chunk boundaries help distinguish chunk/token artefacts from speech.
 windows=[('hit',66,76),('forward',121,134),('intent',140,151),
          ('smash',187,200),('standard',266,280),('purpose',294,307),('closing',388,402.756)]
 import numpy as np, soundfile as sf, torch
 from scipy.signal import resample_poly
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 with ap.batch_asr_lease('cpu'):
  torch.set_num_threads(4)
  model=R/'qwen3-tts/models/whisper-large-v3-turbo'
  if not (model/'config.json').exists():
   from huggingface_hub import try_to_load_from_cache
   model=Path(try_to_load_from_cache('openai/whisper-large-v3-turbo','config.json')).parent
  m=AutoModelForSpeechSeq2Seq.from_pretrained(str(model),dtype=torch.float32,attn_implementation='sdpa',local_files_only=True)
  p=AutoProcessor.from_pretrained(str(model),local_files_only=True)
  recognize=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,device='cpu')
  samples,rate=sf.read(source,dtype='float32')
  rows=[]
  for name,start,end in windows:
   data=samples[round(start*rate):round(end*rate)]
   data=resample_poly(data,1,3).astype(np.float32)
   result=recognize({'array':data,'sampling_rate':16000},generate_kwargs={'language':'korean','task':'transcribe','num_beams':1},return_timestamps=True)
   rows.append({'id':name,'sourceStart':start,'sourceEnd':end,'result':result})
   print(name+': '+result['text'],flush=True)
  ap.save(target,{'sourceSha256':ap.sha(source),'sourceAsrSha256':ap.sha(V/'whole-source-asr.json'),'model':str(model),'device':'cpu','threads':4,'attention':'sdpa','expectedPrompt':None,'windows':rows,'humanListening':False,'rawSourceModified':False})

if __name__=='__main__':main()
