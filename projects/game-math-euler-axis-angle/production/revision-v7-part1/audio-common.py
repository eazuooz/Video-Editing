"""Finite Part1 audio paths, immutable inputs and cooperative GPU lease."""
from pathlib import Path
import hashlib,json,os,subprocess,time,uuid
R=Path(__file__).resolve().parents[4]
P=R/'projects/game-math-euler-axis-angle'
H=Path(__file__).resolve().parent
O=P/'production/local/revision-v7-part1/audio'
LEASE=R/'shared/output/GPU_HANDOFF.json'
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as stream:
  for block in iter(lambda:stream.read(1048576),b''):h.update(block)
 return h.hexdigest()
def rel(path):return Path(path).resolve().relative_to(R).as_posix()
def save(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
 temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 os.replace(temp,path)
def selected(require_full=True):
 control=read(R/'shared/publishing/video-production-control.json')
 # CPU-only preparation is scoped by the explicit approved Part1 artifact.
 # Actual model work still requires the currently selected production guard.
 if require_full:
  claim=control.get('scopedProductionAuthorizations',{}).get(P.name)
  if control['selectedVideo']==P.name:
   assert control['newProductionAuthorization']['fullProductionAuthorized'],'Current production was paused or revoked'
  else:
   assert claim and claim['status']=='explicit-human-authorized-active' and claim['fullProductionAuthorized'],'No active project-scoped human production authority'
  if claim:
   assert claim['status']=='explicit-human-authorized-active' and claim['project']==P.name and claim['part']==1
   auth=R/claim['authorization'];assert auth.resolve()==(H/'authorization.json').resolve()
   assert sha(auth)==claim['authorizationSha256'],'Scoped authorization artifact changed'
   authority=read(auth)
   assert authority['selectedPart']==1 and authority['fullProductionAuthorized'] and authority['scriptApproved']
   assert sha(P/'script/revision-v7-two-part/part-01.ko.json')==authority['approvedScriptSha256']==claim['approvedScriptSha256']
 return control
def validate(require_full=True,preserve_pcm=False):
 selected(require_full);plan=read(P/'planning/revision-v7-two-part/part-01-audio-plan.json')
 assert plan['part']==1 and plan['sceneCount']==21
 for item in plan['immutableInputs'].values():assert sha(R/item['file'])==item['sha256'],'Changed audio input: '+item['file']
 script=read(H/'voice-input.json')
 assert [s['id'] for s in script['scenes']]==[f'v7-a{i:02}' for i in range(1,22)]
 assert sum(len(s['lines']) for s in script['scenes'])==135
 if preserve_pcm:
  for item in plan['preservedV6Pcm']:assert sha(R/item['file'])==item['sha256'],'Prior V6 PCM changed'
 return plan
def gpu():
 out=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.total,utilization.gpu','--format=csv,noheader,nounits'],text=True)
 return list(map(int,out.splitlines()[0].replace(' ','').split(',')))
def clients():
 return subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
def no_foreign_python():
 import psutil
 me=psutil.Process();family={p.pid for p in [me,*me.parents()]}
 current=clients()
 assert not any('python' in row.lower() and int(row.split(',')[0]) not in family for row in current.splitlines()),'Foreign GPU Python is preserved; coordinate before this finite job'
 return current
def wait_memory(minimum,kind):
 samples=[];deadline=time.monotonic()+45;stable=0
 while True:
  selected();free,total,util=gpu();current=no_foreign_python()
  samples.append(dict(time=time.time(),freeMiB=free,totalMiB=total,utilization=util))
  stable=stable+1 if free>=minimum else 0
  if stable>=2:return dict(requiredFreeMiB=minimum,samples=samples,clients=current)
  if time.monotonic()>=deadline:raise RuntimeError(f'{kind}: free VRAM did not reach {minimum}MiB; no foreign process changed')
  print(f'{kind} preload free {free}MiB / {minimum}MiB; stable {stable}/2',flush=True)
  time.sleep(1)
def lease_worker(token):
 import psutil
 state=read(LEASE);me=psutil.Process()
 assert state['token']==token and state['project']==P.name and state['part']==1
 owner=state['coordinator']
 assert any(p.pid==owner['pid'] and abs(p.create_time()-owner['createTime'])<.02 for p in [me,*me.parents()])
 return state
def run_worker(kind,script,cap,minimum):
 import psutil,sys
 validate(preserve_pcm=True);assert not LEASE.exists(),'Existing GPU lease stays untouched'
 before=wait_memory(minimum,kind);me=psutil.Process();token=str(uuid.uuid4())
 control=selected()
 state=dict(token=token,project=P.name,part=1,revision='v7-part1',state=kind+'_running',purpose='One finite Part1 '+kind+' batch',coordinator=dict(pid=me.pid,createTime=me.create_time()),allocatorCapMiB=cap,minimumFreeMiB=minimum,gpuBefore=before,foreignProcessesPaused=[],startedAt=time.time(),implementationSha256=sha(script),commonImplementationSha256=sha(Path(__file__)),observedPrimary=control['selectedVideo'],scopedAuthority=control.get('scopedProductionAuthorizations',{}).get(P.name))
 LEASE.parent.mkdir(parents=True,exist_ok=True)
 with LEASE.open('x',encoding='utf-8') as f:json.dump(state,f)
 code=1
 try:
  with (O/(kind+'-worker.log')).open('ab') as log:
   process=subprocess.Popen([sys.executable,'-u','-X','utf8',str(script),'--worker',token],cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
   state.update(workerPid=process.pid,status='running');save(O/(kind+'-execution.json'),state);code=process.wait()
 finally:
  state.update(status='complete' if code==0 else 'failed',returnCode=code,endedAt=time.time(),foreignProcessesRestored=[])
  save(O/(kind+'-execution.json'),state)
  if LEASE.exists() and read(LEASE).get('token')==token:LEASE.unlink()
 assert code==0,f'{kind} worker failed; inspect preserved log and completed caches before any selected retry'

