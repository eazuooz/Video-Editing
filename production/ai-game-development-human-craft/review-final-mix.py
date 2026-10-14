"""Read back the complete encoded final mix once, in durable complete scenes.

The assembled MP4 copies this AAC stream without further processing. Coverage
includes the un-narrated branding and membership intervals. Cache reuse requires
the identical decoded interval; ASR does not certify human listening.
"""
from pathlib import Path
import json,hashlib,subprocess,uuid,time,os
import numpy as np
import soundfile as sf
import psutil
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft';FLAGS=subprocess.CREATE_NO_WINDOW
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(a):return subprocess.run(a,cwd=ROOT,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=FLAGS)
assert read(ROOT/'shared/publishing/video-production-control.json')['selectedVideo']==SLUG
from revision_paths import workroot
out=workroot(ROOT)/'audio/final-asr';out.mkdir(exist_ok=True)
source=out.parent/'mix.m4a';source_sha=sha(source);data=read(ROOT/f'motion-canvas/src/projects/{SLUG}/scene-data.json')
pcm=out/'encoded-mix-decoded.wav'
decoded_receipt=out/'decoded-input.json'
if pcm.exists():assert decoded_receipt.exists() and read(decoded_receipt)['sourceSha256']==source_sha
else:
 run(['ffmpeg','-v','error','-n','-i',str(source),'-ar','24000','-ac','1',str(pcm)])
 decoded_receipt.write_text(json.dumps({'sourceSha256':source_sha,'pcmSha256':sha(pcm),'sampleRate':24000,'channels':1},indent=2)+'\n')
samples,sr=sf.read(pcm,dtype='float32')
intervals=[('intro',0,2)]+[(s['id'],2+s['start'],2+s['start']+s['duration']) for s in data['scenes']]+[('members',2+sum(s['duration'] for s in data['scenes']),len(samples)/sr)]
lease=ROOT/'shared/output/GPU_HANDOFF.json';assert not lease.exists()
me=psutil.Process();ancestors={x.pid for x in me.parents()};foreign=[x.pid for x in psutil.process_iter(['pid','name']) if (x.info['name'] or '').lower().startswith(('python','train','torchrun')) and x.pid!=me.pid and x.pid not in ancestors];assert not foreign,foreign
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=FLAGS).strip().split(',');assert int(gpu[0])>9000 and int(gpu[1])<40
token=str(uuid.uuid4());record={'token':token,'project':SLUG,'state':'gpu_granted_to_tts','purpose':'final-encoded-mix-complete-ASR','coordinator':{'pid':me.pid,'createTime':me.create_time()},'researchPaused':False}
with lease.open('x',encoding='utf-8') as f:json.dump(record,f,indent=2)
try:
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);local=ROOT/'qwen3-tts/models/whisper-large-v3-turbo';mid=str(local) if (local/'model.safetensors').exists() else 'openai/whisper-large-v3-turbo'
 transcriber=None;results=[]
 for sid,a,b in intervals:
  wave=out/(sid+'.wav');receipt=out/(sid+'.json');portion=samples[round(a*sr):round(b*sr)];decoded_sha=hashlib.sha256(portion.tobytes()).hexdigest()
  if receipt.exists():
   r=read(receipt);assert r['decodedIntervalSha256']==decoded_sha and r['sourceSha256']==source_sha;results.append(r);continue
  sf.write(wave,portion,sr,subtype='PCM_24')
  if transcriber is None:
   model=AutoModelForSpeechSeq2Seq.from_pretrained(mid,dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='sdpa').to('cuda:0');proc=AutoProcessor.from_pretrained(mid)
   transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float16,device='cuda:0')
  raw=transcriber(str(wave),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps=True)
  r={'scene':sid,'start':a,'end':b,'sourceSha256':source_sha,'decodedIntervalSha256':decoded_sha,'text':raw['text'],'segments':raw['chunks']};receipt.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');results.append(r)
  print(sid+': '+raw['text'],flush=True)
 full={'source':str(source.relative_to(ROOT)),'sourceSha256':source_sha,'duration':len(samples)/sr,'coverage':'all decoded encoded audio, intro+28complete scene contexts+member ending; no omitted intervals','scenes':results,'text':' '.join(r['text'] for r in results),'humanListening':'pending','fullTextReview':'pending'}
 (out/'complete-readback.json').write_text(json.dumps(full,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
finally:
 if lease.exists() and read(lease).get('token')==token:
  record.update(state='released',finishedAt=time.time());(out/'gpu-lease-receipt.json').write_text(json.dumps(record,indent=2)+'\n');lease.unlink()
