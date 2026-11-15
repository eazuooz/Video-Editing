"""Retire only our idle launchers; let every actual child finish normally."""
from pathlib import Path
import datetime,hashlib,json,time
import psutil
HERE=Path(__file__).resolve().parent;MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');RUN=MEDIA/'production-resume-20261115T055255Z'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def process(rec,script):
 p=psutil.Process(rec['pid']);assert abs(p.create_time()-rec['createTime'])<.001;assert Path(p.cmdline()[4]).resolve()==HERE/script;return p
def alive(rec):
 try:return bool(rec)and abs(psutil.Process(rec['pid']).create_time()-rec['createTime'])<.001
 except psutil.NoSuchProcess:return False
def main():
 out=RUN/'cooperative-owner-transition-v19.json';assert not out.exists();info=dict(startedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),foreignProcessesModified=False,actualModelsOrRenderersInterrupted=False,newRecurringAutomation=False);paused=[]
 try:
  # This watcher has no model and would otherwise launch an obsolete15% owner.
  wp=MEDIA/'additional-phase-handoff-v17/worker.json'
  if wp.exists():
   w=read(wp)
   if alive(w):
    p=process(w,'run-additional-phase-handoff-v17.py');p.suspend();paused.append(p);assert not read(wp).get('child')and not p.children();p.terminate();p.wait(10);paused.remove(p);info['retiredIdleHandoff']=w
  # Pause only the CPU loop. Its current model child continues uninterrupted.
  wp=MEDIA/'finite-exact12-completion-v13/worker.json';w=read(wp)
  if alive(w):
   p=process(w,'run-finite-exact12-completion-v13.py');p.suspend();paused.append(p);w=read(wp);child=w.get('child');info['preservedCurrentChild']=child;deadline=time.monotonic()+18*60
   while alive(child):
    if time.monotonic()>=deadline:raise TimeoutError('Active child preserved; CPU owner will resume')
    time.sleep(3)
   assert not p.children(recursive=True);p.terminate();p.wait(10);paused.remove(p);info['retiredCpuOwner']=w;info['actualChildEndedNaturally']=True
  # The older finite smoke sequence is only replaced when its exact Python
  # body has no actual Unity/encoder child. Its prior captures remain intact.
  parent=psutil.Process(81608);assert abs(parent.create_time()-1794752210.7730756)<.001 and parent.name().lower()=='pwsh.exe';args=parent.cmdline();assert 'run-native-completion-v6.py'in' '.join(args);parent.suspend();paused.append(parent)
  bodies=[]
  for c in parent.children(recursive=True):
   a=c.cmdline()
   if c.name().lower()=='python.exe'and len(a)>4 and Path(a[4]).resolve()==HERE/'run-native-completion-v6.py'and Path(c.exe()).resolve()==Path('C:/Anaconda3/envs/pytorch-gpu/python.exe'):
    c.suspend();paused.append(c);bodies.append(c)
  assert all(not c.children(recursive=True)for c in bodies),'Actual capture child preserved'
  for c in bodies:c.terminate();c.wait(10);paused.remove(c)
  deadline=time.monotonic()+10
  while parent.children()and time.monotonic()<deadline:time.sleep(.2)
  assert not parent.children();parent.terminate();parent.wait(10);paused.remove(parent);info['retiredIdleNativeSequence']=True
  info['transitionComplete']=True
 finally:
  for p in paused:
   if p.is_running():p.resume()
  info['endedAtUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(info,indent=2)+'\n','utf8');print(json.dumps(info),flush=True)
if __name__=='__main__':main()
