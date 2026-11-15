"""Finite exact12 clean/QA/bundle completion after actual pilot visual reviews."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,time
H=Path(__file__).resolve().parent;ROOT=H.parents[2];M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');B=M/'finite-reviewed-finals-v54';PY=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n','utf8')
def main():
 sp=importlib.util.spec_from_file_location('finite_final_owner',H/'run-camera-native-v1.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g);worker=g.runtime.SingleWorker(path=B/'worker.json');worker.acquire();deadline=time.monotonic()+240*60;pending=[x['slug']for x in read(H/'batch.json')['projects']][4:];done={};held={};child=None;helpers={h:pin(H/h)for h in['run-lesson-film-v37-cooperative-v19.py','verify-encoded-film-v2.py','finalize-local-bundle-v37.py','run-lesson-film-v53-cooperative-v19.py','finalize-local-bundle-v53.py']}
 def run(helper,slug,args,label):
  nonlocal child
  assert pin(H/helper)==helpers[helper];log=B/(slug+'-'+label+'.log');assert not log.exists();log.parent.mkdir(parents=True,exist_ok=True)
  with log.open('w',encoding='utf8')as f:
   child=subprocess.Popen([str(PY),'-u','-X','utf8',str(H/helper),'--project',slug,*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=g.CREATE);worker.update(child=g.identity(child.pid));code=child.wait();worker.update(child=None);child=None
  assert code==0,'Stage failed: '+str(log)
 try:
  while pending:
   g.authority();chosen=None
   for slug in pending[:]:
    base=M/slug;bundle=base/'final-review-v1/bundle.json';visual=base/'film-v10/pilot-visual-review.json'
    if bundle.exists():done[slug]=pin(bundle);pending.remove(slug);continue
    if visual.exists()and read(visual).get('allowedForFinalBundle'):chosen=slug;break
   save(B/'status.json',dict(status='completing-reviewed-local-finals'if chosen else'waiting-for-actual-pilot-visual-review',current=chosen,pending=pending,done=done,held=held,newRecurringAutomation=False))
   if not pending:break
   if chosen:
    try:
     film=M/chosen/'film-v10'
     if not(film/'clean-proof.json').exists():
      assert not(film/'full').exists(),'Preserve incomplete actual clean render';run('run-lesson-film-v53-cooperative-v19.py'if chosen in['shorts-control-destruction-pipeline','shorts-doom-push-forward-healing']else'run-lesson-film-v37-cooperative-v19.py',chosen,['--execute','--mode','full','--wait-minutes','180'],'clean');assert(film/'clean-proof.json').exists()
     if not(film/'clean-encoded-qa.json').exists():run('verify-encoded-film-v2.py',chosen,['--mode','clean'],'clean-qa')
     run('finalize-local-bundle-v53.py'if chosen in['shorts-control-destruction-pipeline','shorts-doom-push-forward-healing']else'finalize-local-bundle-v37.py',chosen,[],'bundle');bundle=M/chosen/'final-review-v1/bundle.json';assert read(bundle)['localFinalBundleComplete'];done[chosen]=pin(bundle)
    except Exception as e:held[chosen]=dict(reason=str(e),noAutomaticRetry=True)
    pending.remove(chosen)
   else:
    if time.monotonic()>=deadline:raise TimeoutError('Finite final wait ended without touching foreign work')
    time.sleep(20)
  save(B/'completion.json',dict(done=done,held=held,newRecurringAutomation=False,humanApproval=False,platformActions=[]));print(json.dumps(dict(finals=len(done),held=held)))
 finally:
  if child is None or child.poll()is not None:worker.close()
if __name__=='__main__':main()
