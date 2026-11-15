"""Wait for the finite existing model chain, then finish two clearer sources."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,time
import psutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');BASE=MEDIA/'mixed-clarity-phase-handoff-v27';PYTHON=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def main():
 s=importlib.util.spec_from_file_location('exact12_handoff_authority',HERE/'run-camera-native-v1.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.runtime.PROTOCOL='exact12-mixed-clarity-handoff-v27';m.runtime.OWNER='exact12-mixed-clarity-handoff';m.authority();worker=m.runtime.SingleWorker(path=BASE/'worker.json');child=None
 try:
  worker.acquire();psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS);names=['run-finite-mixed-clarity-completion-v27.py','run-mixed-clarity-voice-repair-v27.py','run-mixed-clarity-voice-repair-asr-v27.py','review-corrected-voice-captions-v27.py','bind-ready-film-inputs-v27.py','prepare-mixed-clarity-mix-v27.py','run-mixed-clarity-mixed-voice-repair-asr-v27.py','prepare-lesson-mix-v10-cooperative-v19.py','run-lesson-mixed-voice-repair-asr-v10-cooperative-v19.py','cooperative-resource-policy-v19.py','resource-policy-v19.json'];pins=[pin(HERE/n)for n in names];m.save(BASE/'inputs.json',dict(sourceInputs=pins,waitForExistingFiniteChain=True,newRecurringAutomation=False));completion=MEDIA/'inside-phase-handoff-v21/completion.json';deadline=time.monotonic()+240*60
  while not completion.exists():
   m.authority();assert all(pin(x['path'])==x for x in pins)
   if time.monotonic()>=deadline:raise TimeoutError('Existing finite model chain preserved')
   time.sleep(5)
  assert read(completion)['exitCode']==0 and all(pin(x['path'])==x for x in pins);m.authority();child=subprocess.Popen([str(PYTHON),'-u','-X','utf8',str(HERE/'run-finite-mixed-clarity-completion-v27.py')],cwd=ROOT,creationflags=m.CREATE);worker.update(child=m.identity(child.pid));code=child.wait();m.save(BASE/'completion.json',dict(exitCode=code,priorModelJobsPreserved=True,newRecurringAutomation=False));print(json.dumps(dict(mixedClarityOwnerExited=code)),flush=True)
 finally:
  if worker.handle is not None:worker.close(remove=child is None or child.poll()is not None)
if __name__=='__main__':main()
