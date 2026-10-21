"""Approved V8-only immutable inputs and one cooperative finite voice slot."""
from pathlib import Path
import hashlib, json, os, subprocess, time, uuid

R=Path(__file__).resolve().parents[4]
P=R/'projects/game-math-euler-axis-angle'; H=Path(__file__).resolve().parent
O=P/'production/local/revision-v8-orientation-matrix/audio'
LEASE=R/'shared/output/GPU_HANDOFF.json'
SCRIPT=P/'script/revision-v8-orientation-matrix/narration.ko.json'
APPROVED='2cfce716a62d3b951a81a5022dd216ac4cbaafb7b73ffa20e9d0765798e789c3'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
 tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,p)
def selected():
 control=read(R/'shared/publishing/video-production-control.json')
 claim=control.get('scopedProductionAuthorizations',{}).get(P.name)
 assert claim and claim['revision']=='orientation-matrix-v8'and claim['status']=='authorized-production-v8'
 assert claim['fullProductionAuthorized']and claim['ttsAuthorized']and claim['scriptApproved']
 assert claim['approvedScriptSha256']==APPROVED==sha(SCRIPT)
 authority=read(H/'authorization.json')
 assert authority['revision']==claim['revision']and authority['fullProductionAuthorized']and authority['ttsAuthorized']
 assert authority['approvedScriptSha256']==APPROVED and not authority['platformMutation']
 return claim
def validate():
 selected();plan=read(H/'voice-plan.json')
 for item in plan['immutableInputs'].values():assert sha(R/item['file'])==item['sha256'],'Changed voice input: '+item['file']
 script=read(H/'voice-input.json')
 assert len(script['scenes'])==13 and sum(len(s['lines'])for s in script['scenes'])==76
 return plan
def gpu():
 raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.total,utilization.gpu','--format=csv,noheader,nounits'],text=True)
 return list(map(int,raw.splitlines()[0].replace(' ','').split(',')))
def wait_memory(minimum):
 import psutil
 me=psutil.Process();family={p.pid for p in [me,*me.parents()]};deadline=time.monotonic()+45;stable=0;samples=[]
 while True:
  selected();free,total,util=gpu()
  clients=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
  foreign=[line for line in clients.splitlines()if 'python'in line.lower()and int(line.split(',')[0])not in family]
  assert not foreign,'Preserve foreign model work; do not start another GPU model'
  samples.append(dict(freeMiB=free,totalMiB=total,utilization=util,time=time.time()))
  stable=stable+1 if free>=minimum else 0
  if stable>=2:return dict(minimumFreeMiB=minimum,samples=samples,foreignGpuPythonCount=0)
  if time.monotonic()>=deadline:raise RuntimeError('Insufficient stable GPU memory; foreign apps preserved')
  time.sleep(1)
def lease_worker(token):
 import psutil
 d=read(LEASE);me=psutil.Process();owner=d['coordinator']
 assert d['token']==token and d['project']==P.name and d['revision']=='orientation-matrix-v8'
 assert any(p.pid==owner['pid']and abs(p.create_time()-owner['createTime'])<.02 for p in [me,*me.parents()])
def finite_voice_batch():
 import psutil,sys
 plan=validate();assert not LEASE.exists(),'Existing GPU lease remains untouched'
 before=wait_memory(plan['resources']['tts']['minimumFreeMiB']);me=psutil.Process();token=str(uuid.uuid4())
 state=dict(schemaVersion=1,token=token,project=P.name,revision='orientation-matrix-v8',purpose='One finite76-paragraph TTS then13-scene source-ASR batch',
  coordinator=dict(pid=me.pid,createTime=me.create_time()),state='preparing',startedAt=time.time(),gpuBefore=before,
  approvedScriptSha256=APPROVED,voicePlanSha256=sha(H/'voice-plan.json'),foreignProcessesPaused=[],phases=[])
 LEASE.parent.mkdir(parents=True,exist_ok=True)
 with LEASE.open('x',encoding='utf8')as f:json.dump(state,f,indent=2)
 code=1
 try:
  for phase,name in [('tts','voice-render.py'),('source-asr','voice-asr.py')]:
   validate();state['state']=phase+'_running';save(LEASE,state)
   stage=dict(phase=phase,source=rel(H/name),sourceSha256=sha(H/name),startedAt=time.time())
   with(O/(phase+'-worker.log')).open('ab')as log:
    worker=subprocess.Popen([sys.executable,'-u','-X','utf8',str(H/name),'--worker',token],cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    stage['workerPid']=worker.pid;state['phases'].append(stage);save(O/'voice-execution.json',state)
    code=worker.wait();stage.update(returnCode=code,endedAt=time.time());save(O/'voice-execution.json',state)
   assert code==0,phase+' failed; preserve completed takes/caches and inspect the actual cause'
  state['state']='complete'
 finally:
  if code:state['state']='failed'
  state.update(returnCode=code,endedAt=time.time(),foreignProcessesChanged=False)
  save(O/'voice-execution.json',state)
  if LEASE.exists()and read(LEASE).get('token')==token:LEASE.unlink()
 return code
