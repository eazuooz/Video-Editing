"""Two complete-sentence checks only; no expected-script prompt."""
from pathlib import Path
import json,subprocess,hashlib,torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
H=Path(__file__).resolve().parent;P=H.parents[1];L=P/'production/local/room-v3';Q=L/'asr-context';Q.mkdir(exist_ok=True);O=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v3/video');mix=O/'final-mix.m4a';tm=json.loads((L/'timeline.json').read_text('utf8'))['scenes']
torch.set_num_threads(2);model=AutoModelForSpeechSeq2Seq.from_pretrained('openai/whisper-large-v3-turbo',dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cuda:0');processor=AutoProcessor.from_pretrained('openai/whisper-large-v3-turbo',local_files_only=True);recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0');records=[]
previous=H/'asr-context-review.json'
old=json.loads(previous.read_text('utf8')) if previous.exists() else {'records':[]}
for ident,a,b in [('R04',0,4.48),('V31',19.30,25.85)]:
 cached=next((r for r in old['records'] if r['id']==ident and r['relativeInterval']==[a,b]),None)
 if cached:records.append(cached);continue
 row=next(r for r in tm if r['id']==ident);f=Q/(ident+'.wav');subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(row['start']+a),'-i',str(mix),'-t',str(b-a),'-ar','16000','-ac','1','-c:a','pcm_s16le',str(f)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 result=recognize(str(f),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word');records.append({'id':ident,'relativeInterval':[a,b],'file':str(f),'audioSha256':hashlib.file_digest(f.open('rb'),'sha256').hexdigest(),'prompt':None,**result});print(ident,result['text'],flush=True)
(H/'asr-context-review.json').write_text(json.dumps({'mixSha256':hashlib.file_digest(mix.open('rb'),'sha256').hexdigest(),'method':'independent full-sentence ASR, same cached model, no expected prompt','humanListening':False,'records':records},ensure_ascii=False,indent=2),'utf8')
