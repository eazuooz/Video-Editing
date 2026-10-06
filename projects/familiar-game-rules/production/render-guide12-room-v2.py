"""Single authorised correction with the approved CPU Qwen/reference."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,sys,time,traceback
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
REQUEST=BASE/'guide12-room-tts-request-v2.json';STATE=BASE/'guide12-room-tts-execution-v2.json';LOG=BASE/'guide12-room-tts-v2.log'
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
parser=argparse.ArgumentParser();parser.add_argument('--resource',required=True);args=parser.parse_args()
assert not STATE.exists(), 'Inspect state, never repeat an existing worker.'
r=read(ROOT/args.resource);request=read(REQUEST)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and len(request['guides'])==1
assert sha(ROOT/request['textReview'])==request['textReviewSha256']
assert read(ROOT/request['textReview'])['beforeTtsPairedTextReviewed']
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
g=request['guides'][0];assert not (ROOT/g['path']).exists()
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','familiar-game-rules','--check'],cwd=ROOT,check=True)
state=dict(schemaVersion=1,slug='familiar-game-rules',pid=os.getpid(),sessionId=None,commandLine=[sys.executable,*sys.argv],startedAt=now(),
 status='loading-Qwen-for-only12-room-correction',device='cpu',cpuThreads=2,gpuJobs=0,cpuJobs=1,total=1,results=[],
 request=rel(REQUEST),requestSha256=sha(REQUEST),log=rel(LOG),resourceObservation=r,
 finalTimingApproved=False,narrationApproved=False,allOtherSevenPcmPreserved=True,original11PcmPreserved=True,exitCode=None)
def checkpoint():
 sp=BASE/'guide12-room-tts-session-v2.json'
 if sp.exists():
  s=read(sp)
  if s['pid']==os.getpid():state['sessionId']=s['sessionId']
 state['updatedAt']=now();save(STATE,state)
 qp=PROOF.parent/'queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
 if item.get('execution',{}).get('pid')!=os.getpid():item.setdefault('executionHistory',[]).append(item.get('execution',{}))
 running=state['exitCode'] is None
 item.update(stage='only12-source-noun-correction-CPU-Qwen',updatedAt=now(),
  wordCaptionCandidate='projects/familiar-game-rules/production/word-caption-candidate-v1/captions.json',
  guide12RoomCorrection=rel(BASE/'guide12-room-noun-direct-review-v2.json'),
  execution=dict(pid=os.getpid(),commandLine=state['commandLine'],sessionId=state['sessionId'],alive=running,status=state['status'],
   state=rel(STATE),log=rel(LOG),cpuThreads=2,gpuJobs=0,completed=len(state['results']),total=1,activeTasks=['only12-room-correction'] if running else []),
  nextAction='Observe only12 correction exit/currentPCM; whole and independent context plus changed12 join; preserve all original11/other7guide audio and all older ASR. Adjust provisional70paragraph/cut/caption timeline after measurement. No final adoption/mix/render/QA/upload yet.')
 q.update(updatedAt=now(),lastProgressAt=now());save(qp,q)
 for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
  d=read(p)
  for k in ['stage','updatedAt','execution','wordCaptionCandidate','guide12RoomCorrection','nextAction']:d[k]=item[k]
  save(p,d)
original=sys.stdout
class Tee:
 def __init__(self,f):self.f=f
 def write(self,s):original.write(s);original.flush();self.f.write(s);self.f.flush();return len(s)
 def flush(self):original.flush();self.f.flush()
with LOG.open('x',encoding='utf-8') as log:
 sys.stdout=Tee(log);sys.stderr=sys.stdout
 try:
  checkpoint();sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as rn
  rn.configure_project('familiar-game-rules');rn.INFERENCE_DEVICE='cpu';rn.load_tts_dependencies();rn.torch.set_num_threads(2)
  model=rn.Qwen3TTSModel.from_pretrained(str(rn.MODEL_DIR),device_map='cpu',dtype=rn.torch.float32,attn_implementation='eager')
  prompt=model.create_voice_clone_prompt(ref_audio=str(rn.REFERENCE),ref_text=rn.REFERENCE_TEXT_PATH.read_text('utf-8').strip(),x_vector_only_mode=False)
  state['status']='synthesizing-only12-room-correction';checkpoint()
  wavs,rate=model.generate_voice_clone(text=[g['ko']],language=rn.LANGUAGE,voice_clone_prompt=prompt,non_streaming_mode=True,max_new_tokens=rn.MAX_NEW_TOKENS)
  assert len(wavs)==1;p=ROOT/g['path'];p.parent.mkdir(parents=True,exist_ok=True);rn.sf.write(p,wavs[0],rate,subtype='PCM_16')
  pcm,sr=rn.sf.read(p,dtype='float32');assert sr==24000 and len(pcm)>0
  result=dict(id='12',path=g['path'],sha256=sha(p),samples=len(pcm),sampleRate=sr,seconds=len(pcm)/sr,text=g['ko'],en=g['en'],
   tailRatio=rn._tail_ratio(pcm,sr),tailDecayMs=rn._tail_decay_ms(pcm,sr),heuristicIsApproval=False,wholeAsrDirectReview=False,humanListening='pending')
  state['results'].append(result)
  for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
  state.update(status='only12-corrected-measured-awaiting-ASR-context-join',cpuJobs=0,generationComplete=True,allProtectedInputsUnchanged=True,endedAt=now(),exitCode=0)
  checkpoint();print(json.dumps(result,ensure_ascii=False))
 except BaseException:
  state.update(status='failed-only12-room-correction',cpuJobs=0,endedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();traceback.print_exc();raise
 finally:sys.stdout=original;sys.stderr=original
