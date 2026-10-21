"""Finite two-thread V8 audio-only CPU job; preserve the shared GPU owner."""
from pathlib import Path
import argparse,importlib.util,json,os,subprocess,sys,time,uuid
import psutil
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_cpu_audio_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
def main():
 p=argparse.ArgumentParser();p.add_argument('--purpose',required=True);p.add_argument('command',nargs=argparse.REMAINDER);x=p.parse_args()
 command=x.command[1:]if x.command[:1]==['--']else x.command;assert command
 c.selected();lease=c.O/'CPU_HANDOFF.json';assert not lease.exists(),'Preserve another live local audio CPU job'
 assert psutil.virtual_memory().available>=2*1024**3
 me=psutil.Process();token=str(uuid.uuid4());record=dict(token=token,revision='orientation-matrix-v8',purpose=x.purpose,
  coordinator=dict(pid=me.pid,createTime=me.create_time()),state='running',startedAt=time.time(),cpuThreads=2,cudaEnabled=False,foreignJobsChanged=False)
 lease.parent.mkdir(parents=True,exist_ok=True)
 with lease.open('x',encoding='utf8')as f:json.dump(record,f)
 child=None
 try:
  env=dict(os.environ,CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2')
  child=subprocess.Popen(command,cwd=c.R,env=env,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
  record['child']=dict(pid=child.pid,createTime=psutil.Process(child.pid).create_time());c.save(lease,record)
  code=child.wait();record.update(returnCode=code,state='complete'if code==0 else'failed');assert code==0,'Inspect selected CPU job failure; preserve outputs'
 finally:
  record['endedAt']=time.time();live=child is not None and child.poll()is None
  if live:record['state']='owned-child-still-running; explicit completion handoff required'
  c.save(c.O/'jobs'/(token+'.json'),record)
  if lease.exists()and c.read(lease).get('token')==token:
   if live:c.save(lease,record)
   else:lease.unlink()
if __name__=='__main__':main()
