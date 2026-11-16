"""Small CPU ASR flags competing source commentary; never calls it human listening."""
import os,subprocess,sys
os.environ['CUDA_VISIBLE_DEVICES']=''
from prepare import *
def main():
 import torch,numpy as np
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2)
 modelpath=next((pathlib.Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-tiny/snapshots')).iterdir())
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),local_files_only=True,dtype=torch.float32,attn_implementation='eager').to('cpu').eval();proc=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
 pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,device='cpu',dtype=torch.float32)
 sources=read(HERE/'sources.json');unique={};results=[]
 for e in read(HERE/'plan.json')['episodes']:
  for s in e['inserts']:
   key=(s['source'],s['sourceIn'],min(18,s['sourceOut']-s['sourceIn']));unique.setdefault(key,[]).append(s['key'])
 for (source,start,duration),keys in unique.items():
  row=sources[source]
  if not row['hasAudio'] and not row.get('audioFile'):
   results.append(dict(keys=keys,source=source,sourceIn=start,duration=duration,audioPresent=False));continue
  data=subprocess.check_output([FF,'-v','error','-nostdin','-threads','1','-ss',str(start),'-t',str(duration),'-i',row.get('audioFile',row['file']),'-map','0:a:0','-ac','1','-ar','16000','-f','f32le','-'],creationflags=subprocess.CREATE_NO_WINDOW)
  samples=np.frombuffer(data,dtype='<f4').copy();r=pipe(dict(array=samples,sampling_rate=16000),return_timestamps=True,generate_kwargs={'task':'transcribe','max_new_tokens':128})
  results.append(dict(keys=keys,source=source,sourceIn=start,duration=duration,audioPresent=True,text=r['text'],chunks=r.get('chunks'),sourceAudioSha256=row.get('audioSha256',row['sha256']),status='ASR flag for review; music/SFX hallucination possible',humanListening=False))
  print(source,start,r['text'],flush=True)
 save(HERE/'source-audio.json',dict(status='requires-content-review-not-automatic-approval',model=str(modelpath),device='cpu',items=results,humanListening=False))
if __name__=='__main__':main()
