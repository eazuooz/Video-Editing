"""Finite CPU validation only; visual approval remains a separate observed review."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,time
H=Path(__file__).resolve().parent;ROOT=H.parents[2];M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');B=M/'finite-pilot-qa-v45';PY=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n','utf8')
def main():
 sp=importlib.util.spec_from_file_location('finite_qa_owner',H/'run-camera-native-v1.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g);worker=g.runtime.SingleWorker(path=B/'worker.json');worker.acquire();deadline=time.monotonic()+210*60;helper=H/'verify-encoded-film-v2.py';hp=pin(helper);pending=[x['slug']for x in read(H/'batch.json')['projects']][4:];done={};held={};child=None
 try:
  while pending:
   chosen=None
   for slug in pending[:]:
    base=M/slug/'film-v10';proof=base/'pilot-encoded-qa.json'
    if proof.exists():done[slug]=pin(proof);pending.remove(slug);continue
    if(base/'pilot-proof.json').exists():chosen=slug;break
   save(B/'status.json',dict(status='verifying-actual-pilot-frames-and-audio'if chosen else'waiting-for-actual-pilot-proof',current=chosen,pending=pending,done=done,held=held,newRecurringAutomation=False,visualApprovalGranted=False))
   if not pending:break
   if chosen:
    assert pin(helper)==hp;log=B/(chosen+'.log');assert not log.exists();log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w',encoding='utf8')as f:
     child=subprocess.Popen([str(PY),'-u','-X','utf8',str(helper),'--project',chosen,'--mode','pilot'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=g.CREATE);worker.update(child=g.identity(child.pid));code=child.wait();worker.update(child=None);child=None
    proof=M/chosen/'film-v10/pilot-encoded-qa.json'
    if code==0 and proof.exists():done[chosen]=pin(proof)
    else:held[chosen]=dict(exitCode=code,log=pin(log),noAutomaticRetry=True)
    pending.remove(chosen)
   else:
    if time.monotonic()>=deadline:raise TimeoutError('Finite pilot QA wait ended')
    time.sleep(20)
  save(B/'completion.json',dict(done=done,held=held,visualApprovalGranted=False,newRecurringAutomation=False));print(json.dumps(dict(validated=len(done),held=held)))
 finally:
  if child is None or child.poll()is not None:worker.close()
if __name__=='__main__':main()
