"""Finite exact-eleven independent unit/join/paragraph ASR and numeric QA."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,subprocess,time,uuid
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PYTHON=ROOT/'qwen3-tts/.venv/Scripts/python.exe';HELPER=HERE/'run-sentence-asr-v2.py'
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');BASE=MEDIA/'sentence-asr-queue-v2'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');p.add_argument('--wait-minutes',type=float,default=180);a=p.parse_args();assert 0<a.wait_minutes<=180
    spec=importlib.util.spec_from_file_location('ot12_sentence_asr_queue',HELPER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);batch=m.native.authority();slugs=[x['slug']for x in batch['projects']][1:];assert slugs==m.SLUGS[1:]
    inputs=[pin(ROOT/'projects'/slug/'planning/narration-sentence-v2.json')for slug in slugs]
    print(json.dumps(dict(exactSentenceSources=len(inputs),modelsStarted=False,automaticAcceptance=False)),flush=True)
    if not a.execute:return
    worker=m.runtime.SingleWorker(path=BASE/'worker.json');child=None;results=[];deadline=time.monotonic()+a.wait_minutes*60
    try:
        worker.acquire();attempt=BASE/'attempts'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]);attempt.mkdir(parents=True,exist_ok=False);m.save(attempt/'inputs.json',dict(helper=pin(HELPER),sources=inputs))
        for slug in slugs:
            left=(deadline-time.monotonic())/60
            if left<=0:return
            log=attempt/(slug+'.log');m.save(BASE/'status.json',dict(status='guarded-independent-sentence-ASR-child',current=slug,results=results,automaticAcceptance=False))
            argv=[str(PYTHON),'-u','-X','utf8',str(HELPER),'--project',slug]
            with log.open('w',encoding='utf8')as out:
                child=subprocess.Popen(argv+['--execute','--wait-minutes',str(min(180,left))],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));worker.update(child=m.native.identity(child.pid));code=child.wait()
            status=MEDIA/slug/'asr-sentence-v2/status.json';state=read(status)if status.exists()else{};row=dict(slug=slug,exitCode=code,modelComplete=state.get('modelCompleted',False),log=pin(log),voiceAcceptedForFilm=False)
            if row['modelComplete']:
                review=Path(state['review']['path']);row['review']=pin(review);level=review.parent/'levels.json'
                if not level.exists():
                    with (attempt/(slug+'-levels.log')).open('w',encoding='utf8')as out:
                        child=subprocess.Popen(argv+['--levels'],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));worker.update(child=m.native.identity(child.pid));row['levelsExitCode']=child.wait()
                if level.exists():row['levels']=pin(level);row['numericFlags']=read(level)['flags']
            results.append(row);m.save(attempt/'results.json',results);print(json.dumps(row,ensure_ascii=False),flush=True)
            if code or not row['modelComplete'] or row.get('levelsExitCode',0):return
        m.save(BASE/'status.json',dict(status='finite-sentence-ASR-queue-ended',results=results,automaticVoiceAcceptance=False,finalFilmsComplete=False,newRecurringAutomation=False))
    finally:
        if worker.handle is not None:worker.close(remove=child is None or child.poll()is not None)
if __name__=='__main__':main()
