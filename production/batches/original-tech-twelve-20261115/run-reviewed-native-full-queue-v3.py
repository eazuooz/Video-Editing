"""Finite full captures, gated by separate actual-smoke visual reviews."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,subprocess,time,uuid
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PYTHON=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
HELPER=HERE/'run-bounded-native-v3.py'
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
BASE=MEDIA/'reviewed-native-full-queue-v3'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');p.add_argument('--wait-minutes',type=float,default=180);a=p.parse_args();assert 0<a.wait_minutes<=180
    spec=importlib.util.spec_from_file_location('ot12_full_native_queue',HELPER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    cases=['lockon','sand','placement','remaining-seven'];prepared=[]
    for case in cases:
        m.configure(case);r=m.prepare();prepared.append(dict(case=case,fingerprint=r['fingerprint'],base=str(m.BASE)))
    print(json.dumps(dict(stagedCases=len(prepared),newUnityStarted=False,smokeVisualApprovalRequired=True)),flush=True)
    if not a.execute:return
    worker=m.runtime.SingleWorker(path=BASE/'worker.json');child=None;results=[];deadline=time.monotonic()+a.wait_minutes*60
    try:
        worker.acquire();attempt=BASE/'attempts'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]);attempt.mkdir(parents=True,exist_ok=False)
        m.save(attempt/'source-inputs.json',dict(helper=pin(HELPER),cases=prepared,newRecurringAutomation=False))
        for item in prepared:
            review=Path(item['base'])/'smoke-visual-review-v3.json'
            while not review.exists():
                m.save(BASE/'status.json',dict(status='waiting-for-actual-smoke-visual-review',case=item['case'],results=results,unityStarted=False))
                if time.monotonic()>=deadline:return
                time.sleep(min(30,max(0,deadline-time.monotonic())))
            d=read(review);assert d['fingerprint']==item['fingerprint'] and d['actualSourceFramesInspected'] and d['allowedForFullCapture']
            left=(deadline-time.monotonic())/60
            if left<=0:return
            log=attempt/(item['case']+'.log');m.save(BASE/'status.json',dict(status='guarded-full-capture-child',case=item['case'],results=results,visualReview=pin(review)))
            with log.open('w',encoding='utf8')as out:
                child=subprocess.Popen([str(PYTHON),'-u','-X','utf8',str(HELPER),'--case',item['case'],'--execute','--mode','full','--wait-minutes',str(min(180,left))],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));worker.update(child=m.native.identity(child.pid));code=child.wait()
            proof=Path(item['base'])/'accepted-full.json';result=dict(case=item['case'],exitCode=code,log=pin(log),actualFullCaptured=proof.exists(),finalFilmComplete=False)
            if proof.exists():assert read(proof)['fingerprint']==item['fingerprint'];result['proof']=pin(proof)
            results.append(result);m.save(attempt/'results.json',results);print(json.dumps(result),flush=True)
            if code or not proof.exists():return
        m.save(BASE/'status.json',dict(status='finite-full-capture-queue-ended',results=results,finalFilmsComplete=False,newRecurringAutomation=False))
    finally:
        if worker.handle is not None:worker.close(remove=child is None or child.poll()is not None)
if __name__=='__main__':main()
