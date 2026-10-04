"""Independent current mixed windows for observed ambiguous ASR spelling only."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'final-v1';DEST=WORK/'mixed-asr-adaptive-v1';DEST.mkdir(exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();now=lambda:datetime.now(timezone.utc).isoformat()
plan=read(BASE/'measured-edit-v3/plan.json');mix=WORK/'final-mix.wav';settings=read(WORK/'mix-settings.json');assert sha(mix)==settings['wavSha256']
audio,rate=sf.read(mix,dtype='float32',always_2d=True);assert rate==48000 and len(audio)==26693*800
rows=[];state={'pid':os.getpid(),'startedAt':now(),'status':'running','device':'cpu','threads':2,'mixSha256':sha(mix),'totalWindows':4,'completed':0,'automaticApproval':False,'humanListening':'pending'}
def save():state['updatedAt']=now();(WORK/'mixed-asr-adaptive-execution.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
save();torch.set_num_threads(2);mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo';model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu');processor=AutoProcessor.from_pretrained(str(mp));transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
windows=[]
for label,sid,start,end in [('01-first-example','01',20.2,24.15),('02-first-action','02',3,9),('08-title-long','08',0,8),('08-clothing-join','08',15,29)]:
 s=next(s for s in plan['scenes'] if s['id']==sid);windows.append({'label':label,'scene':sid,'from':s['startFrame']/60+start,'to':s['startFrame']/60+end,'independentContext':True})
for w in windows:
 out=DEST/(w['label']+'.wav');sf.write(out,audio[round(w['from']*rate):round(w['to']*rate)].mean(axis=1),rate,subtype='PCM_16');raw=transcriber(str(out),generate_kwargs={'language':'korean','task':'transcribe'},chunk_length_s=30,return_timestamps='word');row={**w,'windowSha256':sha(out),'text':raw['text'],'words':raw['chunks']};rows.append(row);state['completed']=len(rows);save();(DEST/'asr.json').write_text(json.dumps({'mixSha256':settings['wavSha256'],'mix':mix.relative_to(ROOT).as_posix(),'complete':len(rows)==4,'results':rows,'humanListening':'pending','automaticallyApproved':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'label':w['label'],'text':row['text']},ensure_ascii=False),flush=True)
state.update(status='finished-awaiting-direct-content-review',exitCode=0,endedAt=now());save()
