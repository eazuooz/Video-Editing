"""Finite current-task handoff; no recurring automation or model interruption."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,subprocess,time
import psutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');BASE=MEDIA/'inside-phase-handoff-v21';PYTHON=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def alive(r):
 try:return bool(r)and abs(psutil.Process(r['pid']).create_time()-r['createTime'])<.001
 except(psutil.NoSuchProcess,KeyError):return False
def main():
 s=importlib.util.spec_from_file_location('own_phase_authority',HERE/'run-camera-native-v1.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.runtime.PROTOCOL='exact12-inside-phase-handoff-v21';m.runtime.OWNER='exact12-inside-phase-handoff';m.authority();worker=m.runtime.SingleWorker(path=BASE/'worker.json');child=None
 try:
  worker.acquire();wp=MEDIA/'finite-cooperative-completion-v19/worker.json';old=read(wp)if wp.exists()else None;names=['run-finite-inside-completion-v21.py','run-inside-voice-repair-v21-cooperative-v19.py','run-inside-voice-repair-asr-v21-cooperative-v19.py','review-corrected-voice-captions-v21.py','bind-ready-film-inputs-v21.py','prepare-inside-paired-mix-v13-cooperative-v19.py','run-inside-mixed-voice-repair-asr-v13-cooperative-v19.py','cooperative-resource-policy-v19.py','resource-policy-v19.json'];pins=[pin(HERE/n)for n in names];m.save(BASE/'inputs.json',dict(sourceInputs=pins,priorOwner=old,newRecurringAutomation=False));deadline=time.monotonic()+240*60
  while alive(old)or alive((read(wp)if wp.exists()else old or{}).get('child')):
   m.authority();assert all(pin(x['path'])==x for x in pins)
   if time.monotonic()>=deadline:raise TimeoutError('Preserve prior active owner')
   time.sleep(5)
  assert all(pin(x['path'])==x for x in pins);m.authority();child=subprocess.Popen([str(PYTHON),'-u','-X','utf8',str(HERE/'run-finite-inside-completion-v21.py')],cwd=ROOT,creationflags=m.CREATE);worker.update(child=m.identity(child.pid));code=child.wait();m.save(BASE/'completion.json',dict(exitCode=code,priorChildPreserved=True,newRecurringAutomation=False));print(json.dumps(dict(insideCompletionOwnerExited=code)),flush=True)
 finally:
  if worker.handle is not None:worker.close(remove=child is None or child.poll()is not None)
if __name__=='__main__':main()
