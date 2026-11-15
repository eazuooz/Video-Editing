"""One finite exact12 controller: render only actually ready unrepeated local pilots."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,subprocess,time
H=Path(__file__).resolve().parent;ROOT=H.parents[2];M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');B=M/'finite-ready-pilots-v38';PY=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n','utf8')
def main():
 sp=importlib.util.spec_from_file_location('finite_pilot_owner',H/'run-camera-native-v1.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g);worker=g.runtime.SingleWorker(path=B/'worker.json');worker.acquire();deadline=time.monotonic()+180*60;helper=H/'run-lesson-film-v37-cooperative-v19.py';hp=pin(helper);pending=[x['slug']for x in read(H/'batch.json')['projects']][4:];done={};held={};child=None
 try:
  while pending:
   g.authority();chosen=None
   for slug in pending[:]:
    base=M/slug/'film-v10';proof=base/'pilot-proof.json'
    if proof.exists():done[slug]=pin(proof);pending.remove(slug);continue
    if(base/'pilot').exists():held[slug]='Preserved partial pilot requires inspection; no automatic retry';pending.remove(slug);continue
    P=ROOT/'projects'/slug;bp=P/('production/film-inputs-v37.json'if(P/'production/film-inputs-v37.json').exists()else'production/film-inputs-v10.json');bound=read(bp);needed=[Path(bound['nativeFullProofPath']),Path(bound['nativeVisualReviewPath']),Path(bound['mixProofPath']).parent/'mixed-content-review.json']
    if all(x.exists()for x in needed)and read(needed[1]).get('allowedForFilm')and read(needed[2]).get('approvedForPilot'):chosen=slug;break
   save(B/'status.json',dict(status='render-ready-pilots'if chosen else'waiting-for-actual-reviewed-inputs',current=chosen,pending=pending,done=done,held=held,newRecurringAutomation=False))
   if not pending:break
   if chosen:
    assert pin(helper)==hp;log=B/(chosen+'.log');assert not log.exists();log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w',encoding='utf8')as f:
     child=subprocess.Popen([str(PY),'-u','-X','utf8',str(helper),'--project',chosen,'--execute','--mode','pilot','--wait-minutes','180'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=g.CREATE);worker.update(child=g.identity(child.pid));code=child.wait();worker.update(child=None);child=None
    proof=M/chosen/'film-v10/pilot-proof.json'
    if code==0 and proof.exists():done[chosen]=pin(proof)
    else:held[chosen]=dict(exitCode=code,log=pin(log),noAutomaticRetry=True)
    pending.remove(chosen)
   else:
    if time.monotonic()>=deadline:raise TimeoutError('Finite pilot wait ended without touching foreign work')
    time.sleep(20)
  save(B/'completion.json',dict(done=done,held=held,finalVisualReviewStillRequired=True,newRecurringAutomation=False));print(json.dumps(dict(pilots=len(done),held=held)))
 finally:
  if child is None or child.poll()is not None:worker.close()
if __name__=='__main__':main()
