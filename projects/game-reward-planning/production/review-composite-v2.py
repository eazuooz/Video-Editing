"""Serial CPU read-back of current complete scenes and independently cropped joins."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,hashlib,subprocess,sys
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
WORK=BASE/'speech-v2';WORK.mkdir(exist_ok=False)
OUT=ROOT/'shared/output/narration/game-reward-planning/qwen3-1.7b-balanced-v2'
now=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state={'pid':os.getpid(),'startedAt':now(),'status':'running','phase':'current-v2-full-scene-cpu-asr','device':'cpu','threads':2,'gpuJobs':0,'activeTasks':['CPU current-v2 ASR'],'inputLocks':{str(p.relative_to(ROOT).as_posix()):sha(p) for p in [ROOT/'projects/game-reward-planning/script/narration.ko.json',BASE/'repair1/v2-composite-proof.json']},'log':(WORK/'full-asr.log').relative_to(ROOT).as_posix(),'humanListening':'pending'}
def save():
 state['updatedAt']=now();(WORK/'execution.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 qfile=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=json.loads(qfile.read_text(encoding='utf-8'));item=next(x for x in q['items'] if x['slug']=='game-reward-planning')
 item.update(stage=state['phase'],execution={**state,'state':(WORK/'execution.json').relative_to(ROOT).as_posix()},updatedAt=now(),nextAction='Directly compare all13 current-hash scene read-backs and five independent current splice/start contexts, then derive measured cuts and fixed-caption timing; do not synthesize unchanged speech.');q['updatedAt']=now();qfile.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (BASE/'latest-checkpoint.json').write_text(json.dumps({'slug':'game-reward-planning','stage':state['phase'],'execution':state,'nextAction':item['nextAction'],'finalVideoComplete':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save()
command=[sys.executable,'qwen3-tts/review_project_narration.py','--project','game-reward-planning','--manifest','projects/game-reward-planning/production/repair1/v2.manifest.json','--device','cpu','--scenes','02,08']
env=os.environ.copy();env.update(PYTHONUTF8='1',PYTHONIOENCODING='utf-8',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2')
with (WORK/'full-asr.log').open('w',encoding='utf-8') as log:
 worker=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT);state.update(workerPid=worker.pid,command=command);save();code=worker.wait()
assert code==0,f'Full read-back exited {code}'
state.update(phase='current-v2-independent-splice-contexts',fullAsrExitCode=code,workerPid=None,activeTasks=['CPU current-v2 independent joins'],contextsCompleted=[]);save()
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
torch.set_num_threads(2);model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu');p=AutoProcessor.from_pretrained(str(model_path));asr=pipeline('automatic-speech-recognition',model=model,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float32,device='cpu')
rows=[]
for name,sid,a,b in [('02-opening','02',0,3.3),('02-join','02',6.6,14.5),('08-opening','08',0,9.2),('08-join-left','08',6.7,12.6),('08-join-right','08',14.3,21.9)]:
 file=OUT/'chunks'/f'{sid}-scene.wav';x,r=sf.read(file,dtype='float32');crop=WORK/(name+'.wav');sf.write(crop,x[round(a*r):round(b*r)],r,subtype='PCM_16')
 result=asr(str(crop),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word');rows.append({'id':name,'scene':sid,'source':file.relative_to(ROOT).as_posix(),'sourceSha256':sha(file),'from':a,'to':b,**result});state['contextsCompleted'].append(name);save();print(name+': '+result['text'],flush=True)
for p,h in state['inputLocks'].items():assert sha(ROOT/p)==h,'Input changed while reading speech.'
(WORK/'contexts.json').write_text(json.dumps({'rows':rows,'directReview':'pending','humanListening':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
state.update(status='finished-awaiting-current-full-and-join-direct-review',endedAt=now(),exitCode=0,activeTasks=[]);save();print(json.dumps(state,ensure_ascii=False),flush=True)
