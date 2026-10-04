"""CPU readback of all13 final-mix chapters and inserted-pause contexts."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'final-v1';DEST=WORK/'mixed-asr-v1';DEST.mkdir(exist_ok=False)
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();now=lambda:datetime.now(timezone.utc).isoformat()
plan=read(BASE/'measured-edit-v3/plan.json');script=read(BASE.parent/'script/narration.ko.json');mix=WORK/'final-mix.wav';settings=read(WORK/'mix-settings.json');assert sha(mix)==settings['wavSha256']
audio,rate=sf.read(mix,dtype='float32',always_2d=True);assert rate==48000 and len(audio)==plan['finalFrames']*800
rows=[];state={'pid':os.getpid(),'startedAt':now(),'status':'running','device':'cpu','threads':2,'mixSha256':sha(mix),'totalScenes':13,'completed':0,'automaticApproval':False,'humanListening':'pending'}
def save():
 state['updatedAt']=now();(WORK/'mixed-asr-execution.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
 qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qpath);i=next(x for x in q['items'] if x['slug']=='game-reward-planning');i.setdefault('execution',{})['currentMixedAsr']=state.copy();tasks=[x for x in i['execution'].get('activeTasks',[]) if x['kind']!='CPU-current-final-mix-ASR']
 if state['status']=='running':tasks.append({'kind':'CPU-current-final-mix-ASR','pid':os.getpid(),'state':(WORK/'mixed-asr-execution.json').relative_to(ROOT).as_posix(),'log':(BASE/'final-mix-asr-worker.log').relative_to(ROOT).as_posix()})
 i['execution']['activeTasks']=tasks;i['updatedAt']=now();temp=qpath.with_suffix('.mixed-writing');temp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(temp,qpath)
save();torch.set_num_threads(2);mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo';model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu');processor=AutoProcessor.from_pretrained(str(mp));transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
windows=[{'label':'scene-'+s['id'],'scene':s['id'],'from':s['startFrame']/60,'to':(s['startFrame']+s['frames'])/60,'expected':next(x['lines'] for x in script['scenes'] if x['id']==s['id'])} for s in plan['scenes']]
for label,sid,start,end in [('02-opening','02',0,3.3),('08-title','08',0,2.42),('08-left-join','08',10.5,17),('08-right-join','08',19,27),('06-pause','06',4.7,16.6),('10-pause','10',5.5,12),('12-pause','12',10.5,22)]:
 s=next(s for s in plan['scenes'] if s['id']==sid);windows.append({'label':label,'scene':sid,'from':s['startFrame']/60+start,'to':s['startFrame']/60+end,'independentContext':True})
state['totalWindows']=len(windows);save()
for w in windows:
 out=DEST/(w['label']+'.wav');sf.write(out,audio[round(w['from']*rate):round(w['to']*rate)].mean(axis=1),rate,subtype='PCM_16');raw=transcriber(str(out),generate_kwargs={'language':'korean','task':'transcribe'},chunk_length_s=30,return_timestamps='word');row={**w,'windowSha256':sha(out),'text':raw['text'],'words':raw['chunks']};rows.append(row);state['completed']=len(rows);save();(DEST/'asr.json').write_text(json.dumps({'mixSha256':settings['wavSha256'],'mix':mix.relative_to(ROOT).as_posix(),'complete':len(rows)==len(windows),'results':rows,'humanListening':'pending','automaticallyApproved':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'label':w['label'],'text':row['text']},ensure_ascii=False),flush=True)
state.update(status='finished-awaiting-direct-content-review',exitCode=0,endedAt=now());save()
