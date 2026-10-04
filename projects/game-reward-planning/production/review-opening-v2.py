"""Resolve unstable opening-title recognition with independent current PCM crops."""
import hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
import torch,soundfile as sf
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
WORK=BASE/'speech-v2/opening-context';WORK.mkdir(exist_ok=False)
SOURCE=ROOT/'shared/output/narration/game-reward-planning/qwen3-1.7b-balanced-v2/chunks/08-scene.wav'
now=lambda:datetime.now(timezone.utc).isoformat()
state={'pid':os.getpid(),'startedAt':now(),'status':'running','phase':'current-08-opening-independent-cpu-review','device':'cpu','threads':2,'gpuJobs':0,'activeTasks':['CPU08 opening title and first sentence'],'sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'completed':[],'humanListening':'pending'}
def save():
 state['updatedAt']=now();(WORK/'execution.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
 qfile=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=json.loads(qfile.read_text(encoding='utf-8'));item=next(x for x in q['items'] if x['slug']=='game-reward-planning')
 if item['execution']['phase']!=state['phase']:
  previous={**item['execution'],'sessionId':73585};item['executionHistory'].append(previous)
 item.update(stage=state['phase'],execution={**state,'state':(WORK/'execution.json').relative_to(ROOT).as_posix()},updatedAt=now(),nextAction='Compare current08 title/first-sentence independent evidence with unchanged original PCM; directly review13 current full ASRs and seams, then measured paragraph/action timing.');q['updatedAt']=now();qfile.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (BASE/'latest-checkpoint.json').write_text(json.dumps({'slug':'game-reward-planning','stage':state['phase'],'execution':state,'nextAction':item['nextAction'],'finalVideoComplete':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save();torch.set_num_threads(2);mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo';model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu');p=AutoProcessor.from_pretrained(str(mp));asr=pipeline('automatic-speech-recognition',model=model,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float32,device='cpu')
x,r=sf.read(SOURCE,dtype='float32');rows=[]
for name,end in [('08-title',2.42),('08-first-sentence',6.45)]:
 cp=WORK/(name+'.wav');sf.write(cp,x[:round(end*r)],r,subtype='PCM_16');result=asr(str(cp),generate_kwargs={'language':'korean','task':'transcribe','num_beams':5},return_timestamps='word')
 rows.append({'id':name,'sourceSha256':state['sourceSha256'],'from':0,'to':end,**result});state['completed'].append(name);save();print(name+':'+result['text'],flush=True)
(WORK/'asr.json').write_text(json.dumps({'rows':rows,'directReview':'pending','humanListening':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');state.update(status='finished-awaiting-direct-review',exitCode=0,endedAt=now(),activeTasks=[]);save()
