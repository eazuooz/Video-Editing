"""Independent, unprompted ASR of only the ambiguous complete contexts.

CPU inference leaves the active Unity GPU capture alone. This is read-back
evidence; it does not claim a human listened or replace the full cached ASR.
"""
from pathlib import Path
import json,hashlib
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(ROOT/f'projects/{SLUG}/project.json');data=read(ROOT/f'motion-canvas/src/projects/{SLUG}/scene-data.json')
assert read(ROOT/'shared/publishing/video-production-control.json')['selectedVideo']==SLUG
source=ROOT/m['paths']['narration'];out=ROOT/f'shared/output/{SLUG}/ambiguous-contexts';out.mkdir(exist_ok=True)
scenes={s['id']:s for s in data['scenes']};audio,sr=sf.read(source,dtype='float32');source_sha=sha(source)
cases=[('engine-names','02',0,1),('source-attribution','02',4,5),('potion','09',5,5),('genre','10',5,5),('purchase-seventy','17',3,3),('one-impression','22',4,4),('manual-work','26',5,5),('channel-name','28',6,7)]
intervals=[]
for name,sid,first,last in cases:
 s=scenes[sid];a=s['start']+s['paragraphs'][first]['start']-.2;b=s['start']+s['paragraphs'][last]['end']+.25
 intervals.append((name,max(0,a),min(b,len(audio)/sr)))
# Include the preceding complete paragraph, rather than an isolated first word.
intervals.append(('scene03-opening',scenes['02']['start']+scenes['02']['paragraphs'][6]['start']-.2,scenes['03']['start']+scenes['03']['paragraphs'][0]['end']+.25))
torch.set_num_threads(2);transcriber=None;results=[]
for name,a,b in intervals:
 receipt=out/(name+'.json');wav=out/(name+'.wav');stamp={'sourceSha256':source_sha,'start':a,'end':b,'method':'complete-context CPU float32 beam5 segment ASR, no reference prompt'}
 if receipt.exists():
  result=read(receipt);assert result['input']==stamp;results.append(result);continue
 sf.write(wav,audio[round(a*sr):round(b*sr)],sr,subtype='PCM_16')
 if transcriber is None:
  local=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
  mid=str(local) if (local/'model.safetensors').exists() else 'openai/whisper-large-v3-turbo'
  model=AutoModelForSpeechSeq2Seq.from_pretrained(mid,dtype=torch.float32,attn_implementation='eager',use_safetensors=True).to('cpu')
  proc=AutoProcessor.from_pretrained(mid)
  transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,device='cpu',dtype=torch.float32)
 raw=transcriber(str(wav),generate_kwargs={'language':'korean','task':'transcribe','num_beams':5},return_timestamps=True)
 result={'name':name,'input':stamp,'wavSha256':sha(wav),'text':raw['text'],'segments':raw['chunks'],'humanListening':'pending'}
 receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');results.append(result)
 print(name+': '+raw['text'],flush=True)
(out/'review.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
