"""Resolve a concrete extra-greeting/repetition hypothesis at229.5s, not full ASR."""
from pathlib import Path
import os
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
import audio_pipeline as a
H=Path(__file__).resolve().parent
def main():
 a.require_authorized('bounded-final-versus-game-source-audio-investigation')
 root=a.LOCAL/'edit/qa/bounded-audio-216-244';root.mkdir(parents=True,exist_ok=True)
 inputs={};start,end=216.,244.
 for name,source in [('actual-final',a.LOCAL/'edit/encoded-audio-for-asr.wav'),('isolated-game',a.LOCAL/'edit/game-stem.wav')]:
  info=sf.info(source);data,sr=sf.read(source,start=round(start*info.samplerate),stop=round(end*info.samplerate),dtype='float32',always_2d=True)
  data=data.mean(axis=1)
  if sr!=16000:data=resample_poly(data,1,sr//16000)
  target=root/(name+'.wav')
  if not target.exists():sf.write(target,data,16000,subtype='FLOAT')
  else:
   prev,rate=sf.read(target,dtype='float32');assert rate==16000 and np.array_equal(prev,data)
  inputs[name]={'source':a.artifact(source),'window':a.artifact(target),'start':start,'end':end,'reason':'Concrete full-final-ASR inserted extra greeting/repeated prior passage at229.5s. Compare complete28-second context and actual separate game stem; do not assume source-narration preservation excludes commentary.'}
 a.save(root/'inputs.json',inputs)
 os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
 with a.batch_asr_lease('cpu'):
  import torch
  from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
  torch.set_num_threads(4);modelPath=a.ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
  modelId=str(modelPath) if (modelPath/'config.json').is_file() else 'openai/whisper-large-v3-turbo'
  model=AutoModelForSpeechSeq2Seq.from_pretrained(modelId,dtype=torch.float32,attn_implementation='sdpa',local_files_only=True)
  processor=AutoProcessor.from_pretrained(modelId,local_files_only=True)
  recognizer=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
  for name,row in inputs.items():
   dest=root/(name+'-asr.json')
   if dest.exists():assert a.read(dest)['input']==row;continue
   opts={'task':'transcribe','num_beams':1}
   if name=='actual-final':opts['language']='korean'
   print('Recognizing bounded28s '+name,flush=True)
   result=recognizer(str(root/(name+'.wav')),generate_kwargs=opts,return_timestamps=True)
   a.save(dest,{'status':'recognized-pending-direct-review','input':row,'model':modelId,'device':'cpu','threads':4,'expectedPrompt':None,'language':'korean' if name=='actual-final' else 'automatic detection to avoid forcing game dialogue into Korean','text':result['text'],'segments':result['chunks'],'fullVideoAsrRerun':False,'humanListeningClaimed':False})
 print('Two concrete28s contexts recognized once. All original audio/reports preserved.',flush=True)
if __name__=='__main__':main()
