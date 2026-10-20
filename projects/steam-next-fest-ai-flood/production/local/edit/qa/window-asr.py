"""Independent complete-context recognition of two ambiguous windows of the final mix (no chunk stitching)."""
import json, subprocess, sys, torch
from pathlib import Path
R=Path('.').resolve(); L=R/'projects/steam-next-fest-ai-flood/production/local/edit'; wav=L/'qa/final-mix-16k.wav'
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
m='openai/whisper-large-v3-turbo'; model=AutoModelForSpeechSeq2Seq.from_pretrained(m,dtype=torch.float16,low_cpu_mem_usage=True).to('cuda:0'); proc=AutoProcessor.from_pretrained(m)
asr=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,device='cuda:0')
windows={'scene04-59곳':(268,278),'scene04-05-join':(272,296)}; res={}
for k,(a,b) in windows.items():
    w=L/f'qa/window-{k}.wav'; subprocess.run(['ffmpeg','-v','error','-y','-ss',str(a),'-t',str(b-a),'-i',str(wav),str(w)],check=True)
    res[k]={'start':a,'end':b,'text':asr(str(w),generate_kwargs={'language':'korean','task':'transcribe'})['text']}; print(k,res[k]['text'])
json.dump(res,open(L/'qa/window-asr.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
