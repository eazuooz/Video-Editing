"""Blind, complete-sentence contexts for four ambiguous ASR spellings only."""
from pathlib import Path
import json,hashlib
import soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/avoid-game-comparisons';V=P/'production/reference-preserving-v2';O=P/'production/local/reference-preserving-v2/edit';D=O/'qa/ambiguous';D.mkdir(exist_ok=True)
assert json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'))['selectedVideo']==P.name
assert not (R/'shared/output/GPU_HANDOFF.json').exists()
plan=json.loads((V/'edit-plan.json').read_text(encoding='utf8'));sc={s['id']:s for s in plan['scenes']};audio,sr=sf.read(O/'encoded-audio.wav',dtype='float32')
ranges=[('capture-name',sc['07']['voiceStart']+sc['07']['paragraphStarts'][1]-.2,sc['07']['voiceStart']+sc['07']['paragraphStarts'][2]),('collectible',sc['08']['voiceStart']+sc['08']['paragraphStarts'][2]-.2,sc['08']['voiceStart']+sc['08']['paragraphStarts'][3]+3),('scene09-join',sc['08']['voiceStart']+sc['08']['paragraphStarts'][6],sc['09']['voiceStart']+sc['09']['paragraphStarts'][2]),('jump-verb',sc['10']['voiceStart']+sc['10']['paragraphStarts'][2]-.2,sc['10']['voiceStart']+sc['10']['paragraphStarts'][4])]
asr=None;rows=[]
for name,a,b in ranges:
 f=D/(name+'.wav');sf.write(f,audio[round(a*sr):round(b*sr)],sr,subtype='PCM_16');digest=hashlib.sha256(f.read_bytes()).hexdigest();p=D/(name+'.json')
 if p.exists() and json.loads(p.read_text(encoding='utf8'))['sha256']==digest:rows.append(json.loads(p.read_text(encoding='utf8')));continue
 if asr is None:
  import torch
  from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
  torch.set_num_threads(2);mid='openai/whisper-large-v3-turbo';m=AutoModelForSpeechSeq2Seq.from_pretrained(mid,dtype=torch.float16,attn_implementation='eager',local_files_only=True).to('cuda:0');q=AutoProcessor.from_pretrained(mid,local_files_only=True);asr=pipeline('automatic-speech-recognition',model=m,tokenizer=q.tokenizer,feature_extractor=q.feature_extractor,dtype=torch.float16,device='cuda:0')
 result=asr(str(f),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word');row={'name':name,'start':a,'end':b,'sha256':digest,'recognized':result['text'],'expectedTextPrompt':False,'context':'complete sentences surrounding ambiguous passage; not whole-clip repeated recognition','humanListening':False};p.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf8');rows.append(row);print(name,result['text'],flush=True)
(D/'review.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
