"""One whole recognition pass of the final encoded mix, compared against the full script."""
import json, re, difflib, hashlib, subprocess, sys, torch
from pathlib import Path
R=Path('.').resolve(); L=R/'projects/steam-next-fest-ai-flood/production/local/edit'
sys.path.insert(0,str(R/'qwen3-tts'))
video=L/'steam-next-fest-captioned.mp4'; wav=L/'qa/final-mix-16k.wav'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vn','-ac','1','-ar','16000','-c:a','pcm_s16le',str(wav)],check=True)
digest=hashlib.sha256(wav.read_bytes()).hexdigest()
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
local=R/'qwen3-tts/models/whisper-large-v3-turbo'; model_id=str(local) if (local/'model.safetensors').exists() else 'openai/whisper-large-v3-turbo'
dev='cuda:0' if torch.cuda.is_available() else 'cpu'; dtype=torch.float16 if dev!='cpu' else torch.float32
model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=dtype,low_cpu_mem_usage=True).to(dev); proc=AutoProcessor.from_pretrained(model_id)
asr=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,device=dev,chunk_length_s=30,batch_size=4)
out=asr(str(wav),return_timestamps=True,generate_kwargs={'language':'korean','task':'transcribe'})
text=out['text']
sc=json.load(open(R/'projects/steam-next-fest-ai-flood/script/narration.ko.json',encoding='utf-8'))['scenes']; al=json.load(open(R/'projects/steam-next-fest-ai-flood/script/pronunciation.json',encoding='utf-8'))['aliases']
exp=' '.join(l for s in sc for l in s['lines'])
norm=lambda s: re.sub(r'[^가-힣A-Za-z0-9%]','',s)
e=norm(exp); r=norm(text); r2=r
for k,v in al.items(): e=e.replace(norm(k),norm(v)) ; 
sm=difflib.SequenceMatcher(None,e,r); sim=sm.ratio()
diffs=[{'op':op,'script':e[i1:i2],'asr':r[j1:j2]} for op,i1,i2,j1,j2 in sm.get_opcodes() if op!='equal' and (i2-i1>4 or j2-j1>4)]
json.dump({'audioSha256':digest,'videoSha256':hashlib.sha256(video.read_bytes()).hexdigest(),'model':model_id,'device':dev,'similarity':sim,'differences':diffs,'chunks':len(out.get('chunks',[])),'text':text},open(L/'qa/final-mix-asr.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('similarity',round(sim,4),'diffs',len(diffs)); [print(' ',d['op'],d['script'][:40],'|',d['asr'][:40]) for d in diffs[:25]]
