"""Finite exact12 CPU orchestration; no recognizer is loaded in this process."""
from pathlib import Path
import datetime,importlib.util,json,subprocess,time,uuid
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');BASE=MEDIA/'finite-mix-completion-v10';PYTHON=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
VERSIONS={'shorts-journey-sand-sparkle':('voice-repair-v6','asr-repair-v6'),'shorts-horizon-gpu-placement':('voice-master-v8','asr-master-v8'),'shorts-spiderman-swing-anchor':('voice-master-v8','asr-master-v8')}
for slug in ['shorts-control-destruction-pipeline','shorts-returnal-particle-tentacles','shorts-ratchet-dimension-streaming','shorts-doom-push-forward-healing','shorts-botw-chemistry-rules']:VERSIONS[slug]=('voice-repair-v6','asr-repair-v6')
def main():
 s=importlib.util.spec_from_file_location('finite_mix_existing_guard',HERE/'run-camera-native-v1.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.guard.qualifier.BASE=BASE/'resource-observations';worker=m.runtime.SingleWorker(path=BASE/'worker.json');deadline=time.monotonic()+180*60;done={};held={}
 def run(helper,slug,args,log):
  with log.open('w',encoding='utf8')as out:
   p=subprocess.Popen([str(PYTHON),'-u','-X','utf8',str(HERE/helper),'--project',slug,*args],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,creationflags=m.CREATE);worker.update(child=m.identity(p.pid));code=p.wait();worker.update(child=None)
  return code
 try:
  worker.acquire();attempt=BASE/'attempts'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]);attempt.mkdir(parents=True,exist_ok=False);last=None
  while time.monotonic()<deadline:
   m.authority();advanced=False
   for slug,(vv,av)in VERSIONS.items():
    if slug in done or slug in held:continue
    P=ROOT/'projects'/slug;selection=P/'production/accepted-voice-selection-v10.json';voice=MEDIA/slug/vv/'voice-generation-complete-proof.json';status=MEDIA/slug/av/'status.json'
    if not selection.exists():
     if not voice.exists()or not status.exists()or not m.read(status).get('modelCompleted'):continue
     rp=Path(m.read(status)['review']['path']);lp=rp.parent/'levels.json'
     if not lp.exists():continue
     if m.read(lp)['flags']:held[slug]=dict(reason='Numerical voice hold retained',levels=m.pin(lp));continue
     log=attempt/(slug+'-voice-review.log');code=run('review-corrected-voice-captions-v10.py',slug,['--record'],log)
     if code or not selection.exists():held[slug]=dict(reason='Content/whole-word caption review needs an explicit correction',log=m.pin(log));continue
    mix=ROOT/'shared/output/original-tech-twelve-20261115'/slug/'audio-mix-v10/audio-build.json'
    reason=m.busy()
    if reason:last=reason;break
    if not mix.exists():
     log=attempt/(slug+'-mix.log');code=run('prepare-lesson-mix-v10.py',slug,['--execute','--wait-minutes','15'],log)
     if code or not mix.exists():held[slug]=dict(reason='Mix incomplete; preserve outputs without retry',log=m.pin(log));continue
    status=MEDIA/slug/'mixed-asr-v10/status.json'
    if not(status.exists()and m.read(status).get('modelCompleted')):
     if status.exists()and m.read(status).get('modelStarted'):held[slug]=dict(reason='Previously started recognizer needs inspection');continue
     log=attempt/(slug+'-mixed-asr.log');code=run('run-lesson-mixed-voice-repair-asr-v10.py',slug,['--execute','--wait-minutes','15'],log)
     if code or not status.exists()or not m.read(status).get('modelCompleted'):held[slug]=dict(reason='Mixed ASR incomplete; preserve outputs without retry',log=m.pin(log));continue
    done[slug]=dict(mix=m.pin(mix),mixedAsr=m.read(status)['review'],contentAndStereoLevelReviewPending=True);advanced=True;print(json.dumps(dict(project=slug,completedStage=done[slug])),flush=True)
   m.save(BASE/'status.json',dict(status='finite-ready-mix-processing',done=done,held=held,waitReason=last,modelsLoadedInCoordinator=False,newRecurringAutomation=False))
   if len(done)+len(held)==len(VERSIONS):return
   if not advanced:time.sleep(25)
 finally:
  if worker.handle is not None:worker.close()
if __name__=='__main__':main()
