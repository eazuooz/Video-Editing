"""Independent paragraph readback; no expected-script prompt."""
from pathlib import Path
import json,hashlib,gc,torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
H=Path(__file__).resolve().parent;P=H.parents[1];L=P/'production/local/room-v2';Q=L/'asr';Q.mkdir(exist_ok=True)
rows=json.loads((H/'added.ko.json').read_text('utf8'))['scenes'];recognize=None
torch.set_num_threads(2)
for row in rows:
 f=L/'voice/chunks'/(row['id']+'-scene.wav');out=Q/(row['id']+'.json');sha=hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
 if out.exists() and json.loads(out.read_text('utf8'))['audio_sha256']==sha:continue
 if recognize is None:
  model=AutoModelForSpeechSeq2Seq.from_pretrained('openai/whisper-large-v3-turbo',dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cuda:0')
  processor=AutoProcessor.from_pretrained('openai/whisper-large-v3-turbo',local_files_only=True)
  recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0')
 result=recognize(str(f),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 out.write_text(json.dumps({'id':row['id'],'audio_sha256':sha,'model':'openai/whisper-large-v3-turbo','device':'cuda:0','prompt':None,**result},ensure_ascii=False,indent=2),'utf8')
 print(row['id'],result['text'],flush=True);del result;gc.collect();torch.cuda.empty_cache()
