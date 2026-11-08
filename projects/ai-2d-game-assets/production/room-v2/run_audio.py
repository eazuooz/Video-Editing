"""Room-only cooperative admission; never mutate the global guard or foreign apps."""
from pathlib import Path
import json,subprocess,sys,time,uuid,atexit,psutil,os
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/room-v2';L.mkdir(exist_ok=True)
control=json.loads((R/'shared/publishing/video-production-control.json').read_text('utf-8-sig'))
assert control['ai2dRoomRevision20261108']['fullLocalVideoRevisionAuthorized']
sys.path.insert(0,str(R/'qwen3-tts'))
from gpu_handoff_guard import schedule_gpu_handoff
lease=R/'shared/output/GPU_HANDOFF.json'
while True:
 try:schedule_gpu_handoff(P.name,'cuda:0',False,8192);break
 except SystemExit as err:
  free,util=map(int,subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).splitlines()[0].split(','))
  apps=[];block=[]
  for p in psutil.process_iter(['name','exe','cmdline']):
   try:
    name=(p.info['name'] or '').lower();cmd=' '.join(p.info['cmdline'] or [])
    if name in ['overwatch.exe','lunadefense.exe','unrealeditor.exe'] or (name=='unity.exe' and 'Hub/resources' not in str(p.info['exe']).replace('\\','/')):block.append(p.pid)
    if 'python' in name and any(s in cmd for s in ['render_narration.py','run_audio.py','transcribe_reference.py','asr_additions.py']) and p.pid!=os.getpid() and '--cpu' not in cmd and '--device cpu' not in cmd: block.append(p.pid)
    if name in ['discord.exe','chrome.exe','msedge.exe','unity hub.exe']:apps.append({'pid':p.pid,'name':p.info['name']})
   except(psutil.NoSuchProcess,psutil.AccessDenied):pass
  if 'Unregistered GPU activity' in str(err) and not block and free>=10000 and util<=25 and not lease.exists():
   me=psutil.Process();token=str(uuid.uuid4())
   rec={'schemaVersion':1,'token':token,'project':P.name,'state':'tts_running','requestedAt':time.time(),'queueDir':None,'idleGpu':False,'coordinator':{'pid':me.pid,'createTime':me.create_time()},'gpuBeforeTts':{'freeMiB':free,'utilization':util,'minimumFreeMiB':10000},'concurrentAdmission':{'knownApps':apps,'reason':'2026-11-08 root inspected UI-only GPU activity; same already measured 1.7B batch1 profile. Preserve UI, CPU narration, and all foreign work. No global guard change.'}}
   try:
    with lease.open('x',encoding='utf8') as f:json.dump(rec,f,indent=2)
   except FileExistsError:continue
   def release():
    if lease.exists() and json.loads(lease.read_text('utf8')).get('token')==token:lease.unlink()
   atexit.register(release);(H/'gpu-admission.json').write_text(json.dumps(rec,indent=2),'utf8');break
  print('Waiting, preserving work:',str(err),free,util,'blocked',block,flush=True);time.sleep(15)
PY=R/'qwen3-tts/.venv/Scripts/python.exe'
for cmd,log in [([PY,'-X','utf8','-u',R/'qwen3-tts/render_narration.py','--project',P.name,'--manifest',H.relative_to(R)/'tts-manifest.json','--batch-size','1'],'tts.log'),([PY,'-X','utf8','-u',H/'asr_additions.py'],'asr.log')]:
 with (L/log).open('w',encoding='utf8') as f:result=subprocess.run(list(map(str,cmd)),cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 result.check_returncode();print(log,'complete',flush=True)
