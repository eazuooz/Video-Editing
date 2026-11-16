"""ASR corroboration for separated recorder speech; never human listening."""
import os,subprocess
os.environ['CUDA_VISIBLE_DEVICES']=''
from prepare import *
def main():
 import torch,numpy as np
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2)
 modelpath=next((pathlib.Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-tiny/snapshots')).iterdir())
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),local_files_only=True,dtype=torch.float32,attn_implementation='eager').to('cpu').eval();proc=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
 pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,device='cpu',dtype=torch.float32)
 seen={};out=[]
 for key,row in read(HERE/'speech-free-game-audio.json')['items'].items():
  if row['sha256'] in seen:seen[row['sha256']]['keys'].append(key);continue
  data=subprocess.check_output([FF,'-v','error','-nostdin','-threads','1','-i',row['path'],'-ac','1','-ar','16000','-f','f32le','-'],creationflags=subprocess.CREATE_NO_WINDOW)
  r=pipe(dict(array=np.frombuffer(data,dtype='<f4').copy(),sampling_rate=16000),return_timestamps=True,generate_kwargs={'task':'transcribe','max_new_tokens':128})
  result=dict(keys=[key],preparedSha256=row['sha256'],recognizedText=r['text'],chunks=r.get('chunks'),humanListening=False)
  seen[row['sha256']]=result;out.append(result);print(key,r['text'],flush=True)
 save(HERE/'source-audio-residual-review.json',dict(status='ASR evidence for review; non-speech hallucinations possible',items=out,humanListening=False))
if __name__=='__main__':main()
