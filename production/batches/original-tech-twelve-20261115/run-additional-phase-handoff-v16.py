"""Wait for the existing source phase to exit normally, then use one successor."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,subprocess,time
import psutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');RUN=MEDIA/'production-resume-20261115T055255Z';BASE=MEDIA/'additional-phase-handoff-v16';PYTHON=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def alive(record):
 try:return bool(record)and psutil.Process(record['pid']).is_running()and abs(psutil.Process(record['pid']).create_time()-record['createTime'])<.001
 except(psutil.NoSuchProcess,KeyError):return False
def main():
 s=importlib.util.spec_from_file_location('source_handoff_authority',HERE/'run-camera-native-v1.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.runtime.PROTOCOL='original-tech-twelve-additional-phase-handoff-v16';m.runtime.OWNER='original-tech-twelve-source-phase-handoff';m.authority();worker=m.runtime.SingleWorker(path=BASE/'worker.json');child=None
 try:
  worker.acquire();readiness=read(RUN/'additional-completion-readiness-v16.json');assert all(pin(x['path'])==x for x in readiness['sourceInputs']);transition=read(RUN/'idle-mix-coordinator-transition-v13.json');assert not alive(transition['stoppedCpuCoordinator']);oldpath=MEDIA/'finite-exact12-completion-v13/worker.json';old=read(oldpath)if oldpath.exists()else None;deadline=time.monotonic()+120*60
  m.save(BASE/'inputs.json',dict(readiness=pin(RUN/'additional-completion-readiness-v16.json'),oldSourceWorker=old,stoppedIdleMix=pin(RUN/'idle-mix-coordinator-transition-v13.json'),newRecurringAutomation=False));print('Preserving active source jobs; one successor starts after their coordinator exits.',flush=True)
  while True:
   m.authority();fresh=read(oldpath)if oldpath.exists()else old;running=alive(old)or alive((fresh or{}).get('child'))
   if not running:break
   m.save(BASE/'status.json',dict(status='waiting-existing-source-phase-normal-exit',sourceCoordinator=old,actualChildPreserved=(fresh or{}).get('child'),newModelLaunched=False))
   if time.monotonic()>=deadline:raise TimeoutError('Existing source phase remains alive; no replacement was forced')
   time.sleep(20)
  assert all(pin(x['path'])==x for x in readiness['sourceInputs']);m.authority();new=MEDIA/'finite-additional-completion-v16/worker.json'
  if new.exists()and alive(read(new)):print('Existing matching successor preserved; no duplicate launched.',flush=True);return
  m.save(BASE/'status.json',dict(status='existing-source-phase-ended-successor-starting',newRecurringAutomation=False));child=subprocess.Popen([str(PYTHON),'-u','-X','utf8',str(HERE/'run-finite-additional-completion-v16.py')],cwd=ROOT,creationflags=m.CREATE);worker.update(child=m.identity(child.pid));code=child.wait();m.save(BASE/'completion.json',dict(successorExitCode=code,sourcePhaseEndedNaturally=True,modelOrRenderInterrupted=False,newRecurringAutomation=False));print('Single successor exited: '+str(code),flush=True)
 finally:
  if worker.handle is not None:worker.close(remove=child is None or child.poll()is not None)
if __name__=='__main__':main()
