from pathlib import Path
import os,json
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
import audio_pipeline as ap
H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v2'
def main():
 ap.require_authorized('recognize')
 import soundfile as sf,numpy as np,torch
 from scipy.signal import resample_poly
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 source=L/'voice/additional-sample-b.wav';dest=L/'voice/additional-asr.json'
 if dest.exists():print('ASR already exists');return
 with ap.batch_asr_lease('cpu'):
  torch.set_num_threads(4);model=R/'qwen3-tts/models/whisper-large-v3-turbo'
  if not (model/'config.json').exists():
   from huggingface_hub import try_to_load_from_cache
   model=Path(try_to_load_from_cache('openai/whisper-large-v3-turbo','config.json')).parent
  m=AutoModelForSpeechSeq2Seq.from_pretrained(str(model),dtype=torch.float32,attn_implementation='sdpa',local_files_only=True)
  p=AutoProcessor.from_pretrained(str(model),local_files_only=True)
  pipe=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,device=-1)
  y,sr=sf.read(source,dtype='float32');y=resample_poly(y,1,3).astype(np.float32)
  result=pipe({'array':y,'sampling_rate':16000},chunk_length_s=25,stride_length_s=3,generate_kwargs={'language':'korean','task':'transcribe','num_beams':1},return_timestamps='word')
  ap.save(dest,{'sourceSha256':ap.sha(source),'model':str(model),'expectedPrompt':None,'result':result,'humanListening':False})
  print(result['text']);print('words',len(result['chunks']))
if __name__=='__main__':main()
