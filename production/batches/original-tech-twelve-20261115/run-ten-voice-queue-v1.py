"""Finite sequential exact-ten source-voice queue; no recurring automation.

Each child independently checks current authority, exact source pins, full
resource guards, singleton and shared lease immediately before one model run.
Partial or failed generated inputs are preserved, not automatically retried.
"""
from pathlib import Path
import argparse,datetime,importlib.util,json,os,subprocess,time,uuid
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PYTHON=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
BASE=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/ten-voice-queue-v1')
HELPER=HERE/'run-ten-source-voice-v1.py'
def module():
    s=importlib.util.spec_from_file_location('ot12_selected_voice_queue_inputs',HELPER);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');p.add_argument('--wait-minutes',type=float,default=180);a=p.parse_args();assert 0<a.wait_minutes<=180
    helper=module();prepared=[]
    for slug in helper.SLUGS:
        helper.P=ROOT/'projects'/slug;helper.COUNT=len(helper.read(helper.P/'planning/narration-locked-v1.json')['paragraphs'])
        prepared.append(dict(slug=slug,paragraphs=helper.COUNT,fingerprint=helper.inputs()[3]['fingerprint']))
    print(json.dumps(dict(sourceInputsReady=len(prepared),paragraphs=sum(x['paragraphs'] for x in prepared),modelStarted=False)),flush=True)
    if not a.execute:return
    worker=helper.runtime.SingleWorker(path=BASE/'worker.json');child=None;records=[]
    try:
        worker.acquire();deadline=time.monotonic()+a.wait_minutes*60
        attempt=BASE/'attempts'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]);attempt.mkdir(parents=True,exist_ok=False)
        helper.save(attempt/'source-inputs.json',dict(exactPreparedInputs=prepared,helper=helper.pin(HELPER),modelsStarted=False))
        for item in prepared:
            left=(deadline-time.monotonic())/60
            if left<=0:break
            slug=item['slug'];status=dict(status='finite-sequential-voice-queue',current=slug,completedChildren=records,pid=os.getpid(),newRecurringAutomation=False,allFinalFilmsComplete=False)
            helper.save(BASE/'status.json',status)
            log=attempt/(slug+'.log')
            with log.open('w',encoding='utf8') as output:
                child=subprocess.Popen([str(PYTHON),'-u','-X','utf8',str(HELPER),'--project',slug,'--execute','--wait-minutes',str(min(180,left))],cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                worker.update(child=helper.native.identity(child.pid));code=child.wait()
            proof=helper.MEDIA/slug/'voice-v1/voice-generation-complete-proof.json'
            record=dict(slug=slug,exitCode=code,log=helper.pin(log),sourceVoiceGenerated=proof.is_file(),voiceAcceptedForFilm=False)
            if proof.is_file():
                d=helper.read(proof);assert d['fingerprint']==item['fingerprint'];record['proof']=helper.pin(proof)
            records.append(record);helper.save(attempt/'completed-children.json',records);print(json.dumps(record),flush=True)
            # A source/model failure is not automatically retried or treated as
            # an accepted voice. Other explicitly selected sources may progress.
        helper.save(BASE/'status.json',dict(status='finite-queue-ended',completedChildren=records,boundedWaitExpired=time.monotonic()>=deadline,generatedCount=sum(x['sourceVoiceGenerated'] for x in records),finalFilmsComplete=False,newRecurringAutomation=False))
    finally:
        if worker.handle is not None:worker.close(remove=child is None or child.poll() is not None)
if __name__=='__main__':main()
