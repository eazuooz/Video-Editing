"""Finite native Unity render in an isolated project. Preserve the user's live editor."""
from pathlib import Path
import json,sys,subprocess,shutil,uuid,time,psutil
from audio_revision import P,R,guard,read
L=P/'production/local';OWN=R/'unity/VideoEditing/Assets/VideoScenes'/P.name;ISO=L/'unity-capture';LEASE=R/'shared/output/GPU_HANDOFF.json'
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 mode=sys.argv[1] if len(sys.argv)>1 else 'preview';guard();assert not LEASE.exists(),'Existing GPU lease preserved'
 out=L/('capture-'+mode);assert not out.exists(),'Preserve prior capture';out.mkdir(parents=True)
 ISO.mkdir(parents=True,exist_ok=True);shutil.copytree(OWN,ISO/'Assets/VideoScenes'/P.name,dirs_exist_ok=True)
 save(ISO/'Packages/manifest.json',{'dependencies':{'com.unity.modules.imageconversion':'1.0.0'}})
 (ISO/'ProjectSettings').mkdir(exist_ok=True);shutil.copy2(R/'unity/VideoEditing/ProjectSettings/ProjectVersion.txt',ISO/'ProjectSettings/ProjectVersion.txt')
 job={'mode':mode,'output':str(out.resolve()),'timeline':str(P/'production/visual-timing.json'),'sampleFrames':[0,60,300,600,900,1200]};save(out/'job.json',job)
 raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True);free,util=map(int,raw.strip().split(','));assert free>=2000 and util<35,(free,util)
 me=psutil.Process();token=uuid.uuid4().hex;rec={'project':P.name,'token':token,'state':'finite-unity-'+mode,'coordinator':{'pid':me.pid,'createTime':me.create_time()},'gpuBeforeFreeMiB':free,'foreignProcessesPaused':[]}
 with LEASE.open('x',encoding='utf8') as f:json.dump(rec,f)
 proc=None
 try:
  cmd=['C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe','-batchmode','-projectPath',str(ISO.resolve()),'-force-d3d11','-job-worker-count','4','-shadercompiler-threads','2','-executeMethod','YamyamCoding.FlowShort.Editor.FlowCapture.Run','-flowJob',str((out/'job.json').resolve()),'-logFile',str((out/'unity.log').resolve())]
  proc=subprocess.Popen(cmd,creationflags=subprocess.CREATE_NO_WINDOW);print('Unity PID',proc.pid,mode,flush=True);started=time.time()
  while proc.poll() is None:
   time.sleep(5);assert time.time()-started<2400,'Own render timeout'
  assert proc.returncode==0,('Unity failure',proc.returncode);assert (out/'success.json').exists();rec['result']=read(out/'success.json')
  src=ISO/'Assets/VideoScenes'/P.name
  for d in ['Generated','Meshes','Materials','Scenes']:
   shutil.copytree(src/d,OWN/d,dirs_exist_ok=True)
  for p in src.rglob('*.meta'):
   dest=OWN/p.relative_to(src)
   if not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  rec['status']='captured';save(out/'execution.json',rec);print(rec['result'],flush=True)
 finally:
  if proc and proc.poll() is None:proc.terminate();proc.wait(30)
  if LEASE.exists() and read(LEASE).get('token')==token:LEASE.unlink()
if __name__=='__main__':main()
