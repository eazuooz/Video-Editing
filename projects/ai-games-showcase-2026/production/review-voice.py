"""Wait for this one finite voice batch, then recognize its current PCM once."""
from pathlib import Path
import json,time,sys,subprocess,psutil,uuid
R=Path(__file__).resolve().parents[3];P=R/'projects/ai-games-showcase-2026';O=P/'production/local/compact-edit';LEASE=R/'shared/output/GPU_HANDOFF.json';receipt=O/'tts-gpu-coordination.json';out=O/'voice-review-execution.json'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def selected():assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
def save(status,**more):out.write_text(json.dumps({'status':status,'at':time.time(),**more},indent=2)+'\n')
selected();save('waiting-current-owned-voice-batch');deadline=time.time()+7200
while True:
 selected();state=read(receipt)
 if state['state']=='failed':raise RuntimeError('Inspect the failed current voice batch')
 if state['state']=='finished':
  try:alive=abs(psutil.Process(state['coordinator']['pid']).create_time()-state['coordinator']['createTime'])<.01
  except psutil.NoSuchProcess:alive=False
  if not alive:break
 assert time.time()<deadline,'Voice wait timed out; do not alter other applications'
 time.sleep(5)
selected();assert not LEASE.exists(),'Preserve foreign GPU lease'
free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0]);assert free>=5000,free
me=psutil.Process();token=str(uuid.uuid4());owned={'token':token,'project':P.name,'state':'tts_running','coordinator':{'pid':me.pid,'createTime':me.create_time()},'purpose':'one complete current PCM ASR','foreignProcessesPaused':[]}
with LEASE.open('x',encoding='utf8') as f:json.dump(owned,f)
code=1
try:
 save('whole-current-PCM-ASR-running',device='cuda',reuse='matching01/02source-hash caches')
 with (O/'whole-voice-asr.log').open('w',encoding='utf8') as log:
  code=subprocess.call([sys.executable,'-u','-X','utf8','qwen3-tts/review_project_narration.py','--project',P.name,'--manifest','projects/ai-games-showcase-2026/production/tts-manifest.json','--device','cuda'],cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
finally:
 if LEASE.exists() and read(LEASE).get('token')==token:LEASE.unlink()
 save('ASR-ready-for-direct-full-text-review' if code==0 else 'ASR-failed',exitCode=code)
sys.exit(code)
