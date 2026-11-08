"""One model load, complete paragraph readbacks; bound memory to one new passage."""
from pathlib import Path
import json,hashlib,gc,torch,sys
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local';Q=L/'asr';Q.mkdir(exist_ok=True)
plan=json.loads((H/'planning/relations-plan.json').read_text('utf-8'))
cpu='--cpu' in sys.argv;device='cpu' if cpu else 'cuda:0';dtype=torch.float32 if cpu else torch.float16
selected=[x for x in sys.argv[1:] if x.startswith('A')];episodes=[e for e in plan['episodes'] if not selected or e['id'] in selected]
modeldir=R/'qwen3-tts/models/whisper-large-v3-turbo'
modelid=str(modeldir) if modeldir.exists() else 'openai/whisper-large-v3-turbo'
torch.set_num_threads(4 if cpu else 2);recognize=None
for ep in episodes:
 f=L/'voice/chunks'/(ep['id']+'-scene.wav');out=Q/(ep['id']+'.json');sha=hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
 if out.exists() and json.loads(out.read_text('utf-8'))['audio_sha256']==sha:print('Reuse',ep['id'],flush=True);continue
 if recognize is None:
  model=AutoModelForSpeechSeq2Seq.from_pretrained(modelid,dtype=dtype,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to(device)
  processor=AutoProcessor.from_pretrained(modelid,local_files_only=True);recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=dtype,device=device)
 # No expected script prompt; this must be an independent readback.
 result=recognize(str(f),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 data={'id':ep['id'],'audio':str(f),'audio_sha256':sha,'model':modelid,'device':device,'timestampMode':'word','text':result['text'],'chunks':result.get('chunks',[])}
 out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8');(Q/(ep['id']+'.txt')).write_text(result['text']+'\n','utf-8')
 print(ep['id'],result['text'],flush=True);del result;gc.collect()
 if not cpu:torch.cuda.empty_cache()
print(str(len(episodes))+' complete-paragraph readbacks ready for direct text review',flush=True)
