"""One CPU coordinator owns every exact12 model launch, preventing waiter races."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,subprocess,time,uuid
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');BASE=MEDIA/'finite-exact12-completion-v12';PYTHON=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
JOBS=[('shorts-journey-sand-sparkle',None,'run-targeted-voice-repair-asr-v6.py','voice-repair-v6','asr-repair-v6'),('shorts-horizon-gpu-placement',None,'run-master-voice-repair-asr-v8.py','voice-master-v8','asr-master-v8'),('shorts-inside-temporal-antialiasing','run-inside-voice-repair-v7.py','run-inside-voice-repair-asr-v7.py','voice-repair-v7','asr-repair-v7'),('shorts-spiderman-swing-anchor',None,'run-master-voice-repair-asr-v8.py','voice-master-v8','asr-master-v8')]
JOBS += [(s,'run-targeted-voice-repair-v6.py','run-targeted-voice-repair-asr-v6.py','voice-repair-v6','asr-repair-v6')for s in ['shorts-control-destruction-pipeline','shorts-returnal-particle-tentacles','shorts-ratchet-dimension-streaming','shorts-doom-push-forward-healing','shorts-botw-chemistry-rules']]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def main():
 s=importlib.util.spec_from_file_location('single_exact12_existing_guard',HERE/'run-camera-native-v1.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.PROTOCOL='original-tech-twelve-finite-completion-v12';m.OWNER='original-tech-twelve-finite-completion';m.runtime.PROTOCOL=m.PROTOCOL;m.runtime.OWNER=m.OWNER;m.guard.qualifier.BASE=BASE/'resource-observations';m.authority();worker=m.runtime.SingleWorker(path=BASE/'worker.json');deadline=time.monotonic()+180*60;done={};held={};child=None
 def state(stage,slug=None,reason=None):m.save(BASE/'status.json',dict(status=stage,current=slug,reason=reason,done=done,held=held,modelLoadedInCoordinator=False,newRecurringAutomation=False))
 def ready(slug,asr=False):
  last=None
  while True:
   m.authority();reason=m.busy()
   if reason is None and asr:
    raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=m.CREATE);free,use=map(int,raw.splitlines()[0].replace(' ','').split(','));reason='ASR requires9216MiB and utilization below15%'if free<9216 or use>=15 else None
   if reason is None:return
   state('CPU-coordinator-waiting-unchanged-full-guard',slug,reason)
   if reason!=last:print(json.dumps(dict(project=slug,waitReason=reason)),flush=True);last=reason
   if time.monotonic()>=deadline:raise TimeoutError('Finite wait expired; no foreign work was interrupted')
   time.sleep(20)
 def run(helper,slug,args,label):
  nonlocal child
  path=HERE/helper;assert pin(path)==helpers[helper];log=attempt/(slug+'-'+label+'.log');assert not log.exists()
  with log.open('w',encoding='utf8')as out:
   child=subprocess.Popen([str(PYTHON),'-u','-X','utf8',str(path),'--project',slug,*args],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,creationflags=m.CREATE);worker.update(child=m.identity(child.pid));code=child.wait();worker.update(child=None);child=None
  assert code==0,'Stage failed; preserve exact outputs and inspect '+str(log)
  return log
 def completed_asr(status):return status.exists()and read(status).get('modelCompleted')
 def not_started(status):
  if status.exists():assert not read(status).get('modelStarted'),'Previously started incomplete stage needs independent inspection'
 try:
  worker.acquire();attempt=BASE/'attempts'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]);attempt.mkdir(parents=True,exist_ok=False);names={h for _,vh,ah,_,_ in JOBS for h in [vh,ah]if h};names.update(['review-corrected-voice-captions-v10.py','bind-ready-film-inputs-v10.py','prepare-lesson-mix-v10.py','prepare-inside-paired-mix-v11.py','run-lesson-mixed-voice-repair-asr-v10.py','run-inside-mixed-voice-repair-asr-v11.py']);helpers={h:pin(HERE/h)for h in names};m.save(attempt/'inputs.json',dict(coordinator=pin(__file__),helpers=helpers,singleModelLaunchOwner=True,exactProjects=12,newRecurringAutomation=False))
  for slug,vh,ah,vv,av in JOBS:
   try:
    state('source-and-mixed-audio-completion',slug);P=ROOT/'projects'/slug;voice=MEDIA/slug/vv/'voice-generation-complete-proof.json'
    if not voice.exists():
     assert vh;not_started(voice.parent/'status.json');ready(slug);run(vh,slug,['--execute','--wait-minutes','15'],'source');assert voice.exists(),'No model retry after an incomplete source stage'
    status=MEDIA/slug/av/'status.json'
    if not completed_asr(status):not_started(status);ready(slug,True);run(ah,slug,['--execute','--wait-minutes','15'],'source-asr');assert completed_asr(status),'Preserve incomplete source ASR'
    rp=Path(read(status)['review']['path']);lp=rp.parent/'levels.json'
    if not lp.exists():run(ah,slug,['--levels'],'source-levels');assert lp.exists()
    assert not read(lp)['flags'],'Raw/master numerical holds remain active: '+str(lp)
    selection=P/'production/accepted-voice-selection-v10.json'
    if not selection.exists():run('review-corrected-voice-captions-v10.py',slug,['--record'],'voice-content');assert selection.exists()
    if not(P/'production/film-inputs-v10.json').exists():run('bind-ready-film-inputs-v10.py',slug,[],'film-bindings')
    inside='inside'in slug;mv='v11'if inside else'v10';mix=ROOT/'shared/output/original-tech-twelve-20261115'/slug/('audio-mix-'+mv)/'audio-build.json';mixhelper='prepare-inside-paired-mix-v11.py'if inside else'prepare-lesson-mix-v10.py';asrhelper='run-inside-mixed-voice-repair-asr-v11.py'if inside else'run-lesson-mixed-voice-repair-asr-v10.py'
    if not mix.exists():ready(slug);run(mixhelper,slug,['--execute','--wait-minutes','15'],'mix');assert mix.exists(),'Preserve incomplete mix'
    ms=MEDIA/slug/('mixed-asr-'+mv)/'status.json'
    if not completed_asr(ms):not_started(ms);ready(slug,True);run(asrhelper,slug,['--execute','--wait-minutes','15'],'mixed-asr');assert completed_asr(ms),'Preserve incomplete mixed ASR'
    done[slug]=dict(voice=pin(voice),sourceAsr=pin(rp),sourceLevels=pin(lp),mix=pin(mix),mixedAsr=read(ms)['review'],separateStereoContentReviewPending=True,finalFilmComplete=False);print(json.dumps(dict(project=slug,completedAudioStages=done[slug])),flush=True)
   except(AssertionError,FileNotFoundError)as e:
    held[slug]=dict(reason=str(e),failedModelOrAudioStagesNeverRetried=True);print(json.dumps(dict(project=slug,held=held[slug])),flush=True)
   m.save(attempt/'results.json',dict(done=done,held=held))
  state('finite-source-and-mixed-ASR-complete-review-required')
 finally:
  if worker.handle is not None:worker.close(remove=child is None or child.poll()is not None)
if __name__=='__main__':main()
