"""Finite CPU coordinator for remaining exact12 audio; no models in this process."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,subprocess,time,uuid
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');BASE=MEDIA/'finite-lesson-completion-v9';PYTHON=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def main():
 s=importlib.util.spec_from_file_location('finite_exact12_guard',HERE/'run-camera-native-v1.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.guard.qualifier.BASE=BASE/'resource-observations';m.authority();worker=m.runtime.SingleWorker(path=BASE/'worker.json');deadline=time.monotonic()+180*60;results=[]
 def ready():
  last=None
  while True:
   m.authority();reason=m.busy()
   if reason is None:return
   m.save(BASE/'status.json',dict(status='CPU-coordinator-waiting-full-guard',reason=reason,modelLoaded=False,results=results))
   if reason!=last:print(json.dumps(dict(waitReason=reason)),flush=True);last=reason
   if time.monotonic()>=deadline:raise TimeoutError('Finite task wait ended; foreign resources preserved')
   time.sleep(20)
 def run(helper,slug,args,log):
  with log.open('w',encoding='utf8')as out:
   p=subprocess.Popen([str(PYTHON),'-u','-X','utf8',str(HERE/helper),'--project',slug,*args],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,creationflags=m.CREATE);worker.update(child=m.identity(p.pid));code=p.wait();worker.update(child=None)
  return code
 jobs=[('shorts-horizon-gpu-placement',None,'run-master-voice-repair-asr-v8.py','voice-master-v8','asr-master-v8'),('shorts-spiderman-swing-anchor',None,'run-master-voice-repair-asr-v8.py','voice-master-v8','asr-master-v8'),('shorts-inside-temporal-antialiasing','run-inside-voice-repair-v7.py','run-inside-voice-repair-asr-v7.py','voice-repair-v7','asr-repair-v7')]
 jobs += [(s,'run-targeted-voice-repair-v6.py','run-targeted-voice-repair-asr-v6.py','voice-repair-v6','asr-repair-v6')for s in ['shorts-control-destruction-pipeline','shorts-returnal-particle-tentacles','shorts-ratchet-dimension-streaming','shorts-doom-push-forward-healing','shorts-botw-chemistry-rules']]
 try:
  worker.acquire();attempt=BASE/'attempts'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]);attempt.mkdir(parents=True,exist_ok=False)
  m.save(attempt/'inputs.json',dict(adapter=pin(__file__),jobs=[dict(slug=s,source=pin(HERE/v)if v else None,asr=pin(HERE/a))for s,v,a,_,_ in jobs],newRecurringAutomation=False))
  for slug,voice_helper,asr_helper,voice_version,asr_version in jobs:
   vp=MEDIA/slug/voice_version/'voice-generation-complete-proof.json'
   if not vp.exists():
    assert voice_helper;status=vp.parent/'status.json'
    if status.exists():assert not read(status).get('modelStarted'),'Inspect any previously started incomplete model before a new identity'
    ready();code=run(voice_helper,slug,['--execute','--wait-minutes','15'],attempt/(slug+'-source.log'));assert code==0 and vp.exists(),'Incomplete source preserved; no automatic retry'
   status=MEDIA/slug/asr_version/'status.json'
   if not(status.exists()and read(status).get('modelCompleted')):
    if status.exists():assert not read(status).get('modelStarted'),'Preserve incomplete recognizer for review'
    ready();code=run(asr_helper,slug,['--execute','--wait-minutes','15'],attempt/(slug+'-asr.log'));assert code==0 and status.exists()and read(status).get('modelCompleted'),'Incomplete ASR preserved; no automatic retry'
   rp=Path(read(status)['review']['path']);lp=rp.parent/'levels.json'
   if not lp.exists():assert run(asr_helper,slug,['--levels'],attempt/(slug+'-levels.log'))==0 and lp.exists()
   row=dict(slug=slug,voice=pin(vp),asr=pin(rp),levels=pin(lp),flags=read(lp)['flags'],acceptedForFilm=False);results.append(row);m.save(attempt/'results.json',results);print(json.dumps(row),flush=True)
  m.save(BASE/'status.json',dict(status='finite-source-and-ASR-complete-review-required',results=results,newRecurringAutomation=False))
 finally:
  if worker.handle is not None:worker.close()
if __name__=='__main__':main()
