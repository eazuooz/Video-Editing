"""Only11 changed passages, with owned training-boundary handoff and restoration."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,sys,time,traceback
import psutil
ROOT=Path(__file__).resolve().parents[3];CPBASE=Path(__file__).parent;BASE=CPBASE/'revision-balatro60-v2'
STATE=BASE/'narration-tts-execution-v2.json';REQUEST=BASE/'narration-tts-request-v1.json';SESSION=BASE/'narration-tts-session-v2.json'
now=lambda:datetime.now(timezone.utc).isoformat()
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
ap=argparse.ArgumentParser();ap.add_argument('--dry-run',action='store_true');args=ap.parse_args()
import importlib.util
assert Path(sys.prefix).resolve()==(ROOT/'qwen3-tts/.venv').resolve(),'Use the verified dedicated TTS environment before any GPU handoff'
for package in ['soundfile','torch','qwen_tts','psutil']:assert importlib.util.find_spec(package),package
request=read(REQUEST);assert request['pairedWholeTextReview'] and request['overviewPromiseReview'] and len(request['scenes'])==11
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
assert read(ROOT/request['scriptReview'])['contentReadyForApprovedVoiceMeasurement']
assert read(BASE/'source-content-adoption-v7.json')['footageAdoptedForScript']
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as rn
rn.configure_project('presenting-game-scores',str(ROOT/request['manifestOverride']));items=rn.build_render_items(rn.load_jobs())
assert {rel(x.path) for x in items}=={x['path'] for x in request['scenes']}
assert {x.text for x in items}=={x['text'] for x in request['scenes']}
assert not rn.OUTPUT_DIR.exists() and not STATE.exists(),'Existing execution/audio must be inspected, not repeated'
if args.dry_run:print('11 changed items/31 protected inputs/current duplicate/source/script gates verified. Model0/GPU0.',flush=True);raise SystemExit(0)
me=psutil.Process();leasep=ROOT/'shared/output/GPU_HANDOFF.json';lease=read(leasep) if leasep.exists() else None
ancestors={p.pid:p.create_time() for p in [me,*me.parents()]};owner=lease.get('coordinator',{}) if lease else {}
owned=lease and lease.get('project')=='presenting-game-scores' and abs(ancestors.get(owner.get('pid'),-1)-owner.get('createTime',0))<.01
if not owned:
 resource=read(BASE/'voice-resource-before-v2.json');assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
 assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
 save(BASE/'narration-tts-waiting-v2.json',{'schemaVersion':1,'slug':'presenting-game-scores','revision':'balatro60-tetris40-v2','recordedAt':now(),'actualPid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':me.cwd(),'stage':'cooperative-boundary-wait-before-model','modelLoaded':False,'gpuJobs':0,'request':rel(REQUEST),'requestSha256':sha(REQUEST),'foreignLeaseToken':lease.get('token') if lease else None,'sessionId':read(SESSION).get('sessionId') if SESSION.exists() else None,'researchPauseOrProcessChangesByWrapper':0})
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff,check_gpu_handoff
check_gpu_tts_hold('presenting-game-scores','cuda:0',False);schedule_gpu_handoff('presenting-game-scores','cuda:0',False);check_gpu_handoff('presenting-game-scores','cuda:0',False)
for name in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[name]='2'
os.environ.update(TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
lease=read(leasep)
state={'schemaVersion':1,'slug':'presenting-game-scores','revision':'balatro60-tetris40-v2','actualPid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':me.cwd(),'sessionId':read(SESSION).get('sessionId') if SESSION.exists() else None,'startedAt':now(),'stage':'loading-approved-Qwen-under-owned-lease','device':'cuda:0','cpuThreads':2,'gpuJobs':1,'request':rel(REQUEST),'requestSha256':sha(REQUEST),'leaseToken':lease['token'],'researchCoordinator':lease.get('coordinator'),'log':lease.get('ttsLog'),'total':11,'results':[],'activeScene':None,'generationComplete':False,'exitCode':None,'wholeAsrDirectReview':False,'finalMixedAsrApproved':False,'heuristicIsApproval':False,'humanListening':'pending','humanPronunciation':'pending','unchangedSelectedPcmRegenerated':False}
def checkpoint():
 state['updatedAt']=now();save(STATE,state)
 cpPath=CPBASE/'latest-checkpoint.json';cp=read(cpPath)
 job={'pid':state['actualPid'],'createTime':state['createTime'],'commandLine':state['commandLine'],'cwd':state['cwd'],'sessionId':state['sessionId'],'state':rel(STATE),'log':state['log'],'gpu':state['gpuJobs'],'cpuThreads':2,'completed':len(state['results']),'total':11,'workerExpectedRunning':state['exitCode'] is None,'exitCode':state['exitCode']}
 cp.update(recordedAt=now(),stage='single-GPU-selective-Balatro60-voice-measurement' if state['exitCode'] is None else state['stage'],ownedJob=job,nextAction='After actual outer exit, verify exact own lease history and original research restoration; directly compare all11 current voice whole ASR and independent complete contexts. Preserve unchanged PCM, then measured ratios/animation/mix/final pair/QA/collect/private/Git/schedule.');save(cpPath,cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(8):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='presenting-game-scores');item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction']);q.update(updatedAt=now(),lastProgressAt=now())
  if qp.read_text('utf-8-sig')==raw:save(qp,q);break
  time.sleep(.15)
 else:raise RuntimeError('Concurrent queue change; preserve foreign work')
checkpoint()
try:
 rn.INFERENCE_DEVICE='cuda:0';rn.load_tts_dependencies();rn.torch.set_num_threads(2);rn.torch.set_num_interop_threads(1)
 original_load=rn.Qwen3TTSModel.from_pretrained.__func__
 def load(cls,*a,**kw):kw.setdefault('attn_implementation','sdpa');return original_load(cls,*a,**kw)
 rn.Qwen3TTSModel.from_pretrained=classmethod(load)
 original_generate=rn.Qwen3TTSModel.generate_voice_clone;bytext={x['text']:x for x in request['scenes']}
 def generate(self,*a,**kw):
  s=bytext[kw['text'][0]];state.update(stage='synthesizing-'+s['id'],activeScene=s['id']);checkpoint()
  current=rn.torch.cuda.current_stream(self.device);stream=rn.torch.cuda.Stream(device=self.device,priority=-1);stream.wait_stream(current)
  with rn.torch.cuda.stream(stream):result=original_generate(self,*a,**kw)
  stream.synchronize();current.wait_stream(stream);rn.torch.cuda.empty_cache();return result
 rn.Qwen3TTSModel.generate_voice_clone=generate
 original_badness=rn._badness;rn._badness=lambda tail,decay:original_badness(tail,decay) if rn._passes_quality(tail,decay) else 1000000+original_badness(tail,decay)
 original_write=rn.sf.write
 def write(file,data,sr,*a,**kw):
  result=original_write(file,data,sr,*a,**kw);p=Path(file).resolve()
  if p.parent==rn.CHUNK_DIR.resolve() and p.name.endswith('-scene.wav'):
   s=next(x for x in request['scenes'] if (ROOT/x['path']).resolve()==p)
   row={'id':s['id'],'path':rel(p),'sha256':sha(p),'samples':len(data),'sampleRate':sr,'seconds':len(data)/sr,'tailRatio':rn._tail_ratio(data,sr),'tailDecayMs':rn._tail_decay_ms(data,sr),'heuristicIsApproval':False,'wholeAsrApproved':False}
   state['results']=[x for x in state['results'] if x['id']!=s['id']]+[row];checkpoint()
  return result
 rn.sf.write=write;rn.render_chunks(items,1,set());rn.assemble_outputs(rn.load_jobs())
 for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
 assert len(state['results'])==11
 state.update(stage='selective-Balatro60-voice-measured-awaiting-ASR-and-research-resume',generationComplete=True,gpuJobs=0,finishedAt=now(),exitCode=0,totalRawSceneSeconds=sum(x['seconds'] for x in state['results']),allProtectedInputsUnchanged=True,provisionalNarration={'path':rel(rn.FINAL_WAV),'sha256':sha(rn.FINAL_WAV),'timing':rel(rn.TIMING_JSON),'koSrt':rel(rn.FINAL_SRT),'paragraphBoundariesNotFinal':True});checkpoint();print('Changed voice generated; whole/context ASR and actual research restoration still pending.',flush=True)
except BaseException:
 state.update(stage='failed-selective-voice-preserve-chunks',gpuJobs=0,finishedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();traceback.print_exc();raise
