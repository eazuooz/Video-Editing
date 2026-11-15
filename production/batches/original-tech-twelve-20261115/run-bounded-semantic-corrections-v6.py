"""CPU-only finite coordinator; only its guarded named children load models."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,subprocess,time,uuid
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PYTHON=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');BASE=MEDIA/'bounded-semantic-corrections-v6'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def main():
    s=importlib.util.spec_from_file_location('ot12_cpu_coordinator_guard',HERE/'run-bounded-native-v3.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.configure('lockon');m.authority()
    worker=m.runtime.SingleWorker(path=BASE/'worker.json');child=None;results=[];deadline=time.monotonic()+180*60
    def wait_ready():
        last=None
        while True:
            m.authority();reason=m.busy()
            if reason is None:return
            m.save(BASE/'status.json',dict(status='CPU-coordinator-waiting-unchanged-full-resource-guard',reason=reason,modelLoadedInCoordinator=False,results=results))
            if reason!=last:print(json.dumps(dict(status='waiting-for-actual-full-resource-guard',reason=reason)),flush=True);last=reason
            if time.monotonic()>=deadline:raise TimeoutError('Finite coordinator deadline; no job was forced')
            time.sleep(min(10,max(0,deadline-time.monotonic())))
    def run(helper,slug,args,log):
        with log.open('w',encoding='utf8')as out:
            process=subprocess.Popen([str(PYTHON),'-u','-X','utf8',str(HERE/helper),'--project',slug,*args],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));worker.update(child=m.native.identity(process.pid));code=process.wait()
        return code
    try:
        worker.acquire();attempt=BASE/'attempts'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]);attempt.mkdir(parents=True,exist_ok=False)
        m.save(attempt/'inputs.json',dict(voiceAdapter=pin(HERE/'run-targeted-voice-repair-v6.py'),asrAdapter=pin(HERE/'run-targeted-voice-repair-asr-v6.py'),bootstrapIdentityReview=pin(MEDIA/'production-resume-20261115T055255Z/bootstrap-parent-identity-review-v1.json'),newRecurringAutomation=False))
        for slug in ['shorts-journey-sand-sparkle', 'shorts-horizon-gpu-placement', 'shorts-inside-temporal-antialiasing', 'shorts-spiderman-swing-anchor', 'shorts-control-destruction-pipeline', 'shorts-returnal-particle-tentacles', 'shorts-ratchet-dimension-streaming', 'shorts-doom-push-forward-healing', 'shorts-botw-chemistry-rules']:
            wait_ready();log=attempt/(slug+'-source.log');code=run('run-targeted-voice-repair-v6.py',slug,['--execute','--wait-minutes','15'],log)
            proof=MEDIA/slug/'voice-repair-v6/voice-generation-complete-proof.json';assert code==0 and proof.exists(),'Source incomplete/held: preserve outputs; no automatic retry'
            row=dict(slug=slug,voiceProof=pin(proof),voiceLog=pin(log),voiceAcceptedForFilm=False);m.save(BASE/'status.json',dict(status='new-source-complete-independent-ASR-next',current=slug,results=results,voiceProof=pin(proof)))
            wait_ready();log=attempt/(slug+'-asr.log');code=run('run-targeted-voice-repair-asr-v6.py',slug,['--execute','--wait-minutes','15'],log)
            status=MEDIA/slug/'asr-repair-v6/status.json';assert code==0 and read(status).get('modelCompleted'),'Independent ASR incomplete; preserve outputs'
            review=Path(read(status)['review']['path']);row.update(asrReview=pin(review),asrLog=pin(log));level=review.parent/'levels.json'
            if not level.exists():
                code=run('run-targeted-voice-repair-asr-v6.py',slug,['--levels'],attempt/(slug+'-levels.log'));assert code==0 and level.exists()
            row.update(levels=pin(level),numericFlags=read(level)['flags']);results.append(row);m.save(attempt/'results.json',results);print(json.dumps(row,ensure_ascii=False),flush=True)
        m.save(BASE/'status.json',dict(status='finite-targeted-source-QA-complete',results=results,automaticSpeechAcceptance=False,finalFilmsComplete=False,newRecurringAutomation=False))
    finally:
        if worker.handle is not None:worker.close(remove=child is None or child.poll()is not None)
if __name__=='__main__':main()
