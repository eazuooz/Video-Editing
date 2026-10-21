"""One cooperative finite NVENC batch; never stops another process or queue."""
from pathlib import Path
import importlib.util,json,os,sys,subprocess,time,uuid
import psutil
H=Path(__file__).parent
sp=importlib.util.spec_from_file_location('v8_render_slot_common',H/'common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
LEASE=c.R/'shared/output/GPU_HANDOFF.json'
def main():
 c.authorized();args=sys.argv[1:];assert args==['--all']or(len(args)==2 and args[0]=='--paragraph')
 assert not LEASE.exists(),'Another finite resource owner is active; preserve its job'
 raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.total,utilization.gpu','--format=csv,noheader,nounits'],text=True);free,total,util=map(int,raw.splitlines()[0].replace(' ','').split(','));assert free>=3072
 me=psutil.Process();state=dict(schemaVersion=1,owner='game-math-orientation-matrix-v8-render',project=c.P.name,revision='orientation-matrix-v8',token=str(uuid.uuid4()),purpose='Finite selected paragraph video composition',coordinator=dict(pid=me.pid,createTime=me.create_time()),arguments=args,startedAt=time.time(),gpuBefore=dict(freeMiB=free,totalMiB=total,utilization=util),foreignProcessesChanged=False)
 LEASE.parent.mkdir(parents=True,exist_ok=True)
 with LEASE.open('x',encoding='utf8')as f:json.dump(state,f,indent=2)
 code=1
 try:
  p=subprocess.Popen([sys.executable,'-u','-X','utf8',str(H/'compose.py'),*args,'--codec','h264_nvenc'],cwd=c.R,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
  state['workerPid']=p.pid;state['state']='running';c.save(c.O/'edit/render-execution.json',state);code=p.wait();assert code==0
 finally:
  state.update(returnCode=code,endedAt=time.time(),state='complete'if code==0 else'failed');c.save(c.O/'edit/render-execution.json',state)
  if LEASE.exists()and c.read(LEASE).get('token')==state['token']:LEASE.unlink()
 return code
if __name__=='__main__':raise SystemExit(main())
