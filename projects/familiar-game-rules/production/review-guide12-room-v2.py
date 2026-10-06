"""One CPU2 worker for the changed12 whole or its reviewed context plan."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,sys,time,traceback
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
parser=argparse.ArgumentParser();parser.add_argument('--resource',required=True);parser.add_argument('--phase',choices=['whole','contexts'],required=True);args=parser.parse_args()
r=read(ROOT/args.resource);assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'].replace('Z','+00:00'))).total_seconds()<240
tts=read(BASE/'guide12-room-tts-execution-v2.json');assert tts['exitCode']==0 and tts['actualExitObserved']
request=read(BASE/'guide12-room-tts-request-v2.json');assert sha(BASE/'guide12-room-tts-request-v2.json')==tts['requestSha256']
if args.phase=='whole':
 a=tts['results'][0];g=request['guides'][0]
 contexts=[dict(id='12-whole',sourcePath=a['path'],sourceSha256=a['sha256'],seconds=a['seconds'],expectedKo=g['ko'],expectedEn=g['en'])]
else:
 context_plan=read(BASE/'guide12-room-context-plan-v2.json')
 assert sha(ROOT/context_plan['wholeReview'])==context_plan['wholeReviewSha256'] and read(ROOT/context_plan['wholeReview'])['wholeDirectReview']
 contexts=context_plan['contexts'];assert len(contexts)==2
STATE=BASE/f'guide12-room-{args.phase}-asr-execution-v2.json';LOG=BASE/f'guide12-room-{args.phase}-asr-v2.log'
dest=BASE/f'guide12-room-{args.phase}-asr-v2'
assert not STATE.exists() and not dest.exists();dest.mkdir()
for c in contexts:assert sha(ROOT/c['sourcePath'])==c['sourceSha256']
state=dict(schemaVersion=1,slug='familiar-game-rules',pid=os.getpid(),sessionId=None,commandLine=[sys.executable,*sys.argv],startedAt=now(),
 status='loading-local-CPU-whisper-changed12-'+args.phase,cpuThreads=2,gpuJobs=0,total=len(contexts),completed=0,exitCode=None,
 resourceObservation=r,contexts=contexts,log=rel(LOG),expectedWasRecognizerPrompt=False,automaticApproval=False,
 directReview=False,narrationApproved=False,allOtherAudioAsrRepeated=False,humanWholeListening='pending',pronunciation='pending')
def checkpoint():
 sp=STATE.with_name(STATE.stem+'.session.json')
 if sp.exists():
  s=read(sp)
  if s['pid']==os.getpid():state['sessionId']=s['sessionId']
 state['updatedAt']=now();save(STATE,state)
 qp=PROOF.parent/'queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
 if item.get('execution',{}).get('pid')!=os.getpid():item.setdefault('executionHistory',[]).append(item.get('execution',{}))
 running=state['exitCode'] is None
 item.update(stage='only12-corrected-'+args.phase+'-CPU-ASR',updatedAt=now(),execution=dict(pid=os.getpid(),commandLine=state['commandLine'],
  sessionId=state['sessionId'],alive=running,status=state['status'],state=rel(STATE),log=rel(LOG),cpuThreads=2,gpuJobs=0,
  completed=state['completed'],total=state['total'],activeTasks=['only12-corrected-'+args.phase+'-ASR'] if running else []),
  nextAction='Directly read changed12 current whole words/end, then its complete independent ending and changed join. Preserve original11/other7audio/oldASR; update measured source/cue candidate only after review. Final mix/render/QA/private pending.')
 q.update(updatedAt=now(),lastProgressAt=now());save(qp,q)
 for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
  d=read(p)
  for k in ['stage','updatedAt','execution','nextAction']:d[k]=item[k]
  d.update(asrApproved=False,narrationApproved=False,finalRatioApproved=False);save(p,d)
original=sys.stdout
class Tee:
 def __init__(self,f):self.f=f
 def write(self,s):original.write(s);original.flush();self.f.write(s);self.f.flush();return len(s)
 def flush(self):original.flush();self.f.flush()
with LOG.open('x',encoding='utf-8') as log:
 sys.stdout=Tee(log);sys.stderr=sys.stdout
 try:
  checkpoint();import torch
  from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
  torch.set_num_threads(2);mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
  model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
  processor=AutoProcessor.from_pretrained(str(mp),local_files_only=True)
  transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
  for c in contexts:
   state['status']='transcribing-'+c['id'];checkpoint()
   raw=transcriber(str(ROOT/c['sourcePath']),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   row={**c,'text':raw['text'],'words':raw['chunks'],'expectedWasRecognizerPrompt':False,'directReview':False,'approved':False}
   assert sha(ROOT/c['sourcePath'])==c['sourceSha256'];save(dest/(c['id']+'.json'),row)
   state['completed']+=1;checkpoint();print(json.dumps(dict(id=c['id'],text=raw['text']),ensure_ascii=False))
  state.update(status='closed-changed12-'+args.phase+'-awaiting-direct-review',exitCode=0,endedAt=now());checkpoint()
 except BaseException:
  state.update(status='failed-changed12-'+args.phase,exitCode=1,endedAt=now(),error=traceback.format_exc());checkpoint();traceback.print_exc();raise
 finally:sys.stdout=original;sys.stderr=original
