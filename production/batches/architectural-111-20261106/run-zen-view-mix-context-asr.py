"""Finite blind P5/P7 complete-context review of the exact07.04 stereo mix.

Default verifies metadata/byte pins only. --execute may extract exactly two
different, complete paragraph windows and launch the approved recognizer under
its existing GPU guard. No TTS, same-input repetition, source editing, alias,
expected prompt, whole-mix coverage claim or automatic listening approval.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,math,os,subprocess,sys,time,uuid
from pathlib import Path
sys.dont_write_bytecode=True
import psutil
from initialize import ROOT,HERE,MEDIA,AUTH_KEY,read,save

FULL_SHA='72d5d0c13c7507f775447b989c536b75c6b7235837a0e3424771d8bd48c2dee3'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
if sha(HERE/'run-zen-view-mix-asr.py')!=FULL_SHA:raise RuntimeError('Reviewed full-mix recognizer adapter changed')
full=module('zen_context_approved_fullmix_primitives',HERE/'run-zen-view-mix-asr.py');qa=full.qa;raw=full.raw
PROTOCOL='architectural111-07-04-mix-context-asr-v1';OWNER='architectural-111-07-04-mix-context-asr'
runtime=module('zen_context_isolated_singleton',HERE/'run-first-native.py');runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER
TOPIC=MEDIA/'shorts-leveldesign-07-04';PROJECT=ROOT/'projects/shorts-leveldesign-07-04'
WORKER=MEDIA/'07-04-mix-context-asr-worker.json';STATE=MEDIA/'07-04-mix-context-asr-progress.json'
PARAGRAPHS=(5,7)
PROFILE=dict(qa.PROFILE,inputKind='actual-final-stereo-mix-complete-paragraph-context',
 stereoDownmix=full.PROFILE['stereoDownmix'],coverage='Only complete authored paragraphs5and7; not whole-mix coverage',
 inputSampleRate=48000,paragraphIndices=list(PARAGRAPHS),expectedTextUse='comparison metadata only; never recognizer prompt')
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)

def require(v,reason):
 if not v:raise ValueError(reason)

def authorize():
 control=read(ROOT/'shared/publishing/video-production-control.json')[AUTH_KEY];batch=read(HERE/'batch.json')
 require(control['status']not in('paused','stopped','cancelled')and control['automaticAdvanceWithinExactList']and not control['automaticAdvanceOutsideList']and control['humanFinalReviewRequired']and not control['youtubeAuthorized'],'Selected finite local-only111 authorization inactive')
 require(batch['localFinalReviewOnly']and len(batch['projects'])==111 and any(r['topicId']=='07.04'for r in batch['projects']),'Context task is outside selected07.04 scope')

def context_tasks(voice,levels,mix,draft):
 """Use unchanged strict full-coverage metadata guards, then select P5/P7."""
 all_tasks=full.coverage(voice,levels,mix);takes=[t for t in all_tasks if t['kind']=='take'];result=[]
 require(len(draft['narrationKo'])==7,'Exact seven authored paragraphs required')
 for n in PARAGRAPHS:
  group=[t for t in takes if t['paragraphIndex']==n]
  require(group,'Missing complete contextual paragraph')
  expected=' '.join(t['expected']for t in group);require(expected==draft['narrationKo'][n-1],'Context text must retain the full exact paragraph')
  declared=[p for p in levels.get('paragraphs',[])if p['paragraph']==n]
  require(len(declared)==1,'One accepted line-level paragraph descriptor required')
  a,b=group[0]['beginSample'],group[-1]['endSample'];p=declared[0]
  require(p['sceneIds']==[t['sceneId']for t in group]and p['destinationSampleRange']==[a//2,b//2],'Paragraph boundary differs from accepted component sample grid')
  require(a%2==b%2==0 and 0<=a<b<=mix['frames'],'Exact doubled raw paragraph boundary required')
  result.append(dict(key=f'mix-context-p{n:03}',kind='complete-paragraph-context',paragraphIndex=n,sceneIds=p['sceneIds'],path=mix['path'],audioSHA256=mix['sha256'],beginSample=a,endSample=b,offsetSample=a,offsetSeconds=a/48000,durationSeconds=(b-a)/48000,expected=expected,expectedComparisonOnly=True))
 require([t['paragraphIndex']for t in result]==[5,7]and len(result)==2,'Only two authorized complete-context tasks supported')
 return result,all_tasks

def baseline_review(path,job,build,voice,metadata_tasks):
 """Verify existing67task records without running/writing full.summary()."""
 path=Path(path).resolve();folder=Path(job['output']).resolve();require(path==folder/'review.json','Use exact current full-mix review path')
 require(job['protocol']==full.PROTOCOL and digest(job['identity'])==job['fingerprint'],'Full-mix source job identity changed')
 ident=job['identity'];mix=build['mixWav']
 require(ident['audioBuildFingerprint']==build['fingerprint']and ident['audioBuildSHA256']==sha(Path(build['output'])/'audio-build.json')and ident['mix']==mix and ident['voiceFingerprint']==voice['fingerprint'],'Baseline recognition belongs to another mix/voice')
 require(ident['adapterSHA256']==FULL_SHA and Path(job['modelPath']).resolve()==qa.MODEL.resolve()and ident['profile']==full.PROFILE and ident['modelPins']==qa.APPROVED['modelPins']and ident['trustedUtilitySHA256']==qa.APPROVED['trustedSHA256'],'Baseline recognizer profile/model differs')
 require(len(ident['tasks'])==len(metadata_tasks),'Baseline task coverage differs')
 for actual,expected in zip(ident['tasks'],metadata_tasks):
  require(all(actual.get(k)==v for k,v in expected.items()),'Baseline exact component/join clock differs')
 for p in job['sourcePins']:require(sha(p['path'])==p['sha256'],'Baseline ASR source/guard pin changed')
 records=[full.cached(job,t)for t in ident['tasks']];require(all(r is not None for r in records),'Original full-mix task records incomplete')
 takes=[r for r in records if r['task']['kind']=='take'];joins=[r for r in records if r['task']['kind']=='boundary'];count=len(voice['identity']['scenes'])
 require(len(takes)==count and len(joins)==count-1,'Original take/join coverage changed')
 value=read(path)
 require(value.get('status')=='mixed-asr-complete-literal-and-listening-review-pending'and value.get('takes')==takes and value.get('boundaryWindows')==joins and value.get('fingerprint')==job['fingerprint']and value.get('mixSHA256')==mix['sha256']and value.get('voiceFingerprint')==voice['fingerprint']and value.get('fullActualMixCoverage')is True and value.get('coveredSamples')==mix['frames'],'Baseline review differs from actual immutable task caches')
 for key in ('aliasesApplied','rawVoiceRecognitionReusedAsMix','normalizedStemRecognized','automaticSpeechPass','humanListening','finalApproval'):require(value.get(key)is False,'Baseline cannot supply altered or approved recognition')
 return pin(path)

def prepare_metadata(audio_path,review_path):
 authorize()
 path=Path(audio_path).resolve();require(path.name=='audio-build.json'and path.is_relative_to((TOPIC/'audio-preparation-v1').resolve()),'Only selected accepted07.04 audio build supported')
 build=read(path);folder=path.parent;require(build.get('topicId')=='07.04'and build.get('schemaVersion')=='07-04-audio-build-v1'and Path(build['output']).resolve()==folder,'Wrong selected audio source')
 recipe=read(folder/'input-recipe.json');require(recipe['fingerprint']==build['fingerprint']and full.audio.digest(recipe['identity'])==build['fingerprint'],'Accepted recipe fingerprint differs')
 proposal=recipe['proposal'];require(full.audio.digest(proposal['identity'])==proposal['fingerprint']==recipe['identity']['proposalFingerprint']and proposal['identity']['processorSHA256']==full.AUDIO_SHA,'Accepted scalar/music producer identity changed')
 for p in proposal['identity']['sourcePins']:require(sha(p['path'])==p['sha256'],'Accepted source/voice/music evidence changed')
 acceptance=recipe['identity']['acceptedReview'];require(sha(acceptance['path'])==acceptance['sha256'],'Accepted component review changed')
 require(full.audio.accepted_review(proposal,acceptance['path'],build['rawVoiceAsr'],build['rawNumericalLevelReview'])==recipe['acceptedReview'],'Exact accepted component decisions changed')
 require(full.audio.reuse_audio(folder,recipe)==build,'Accepted audio artifacts changed')
 voice=read(full.audio.VOICE);require(build['rawVoice']==voice['aggregateWav']and build['rawVoiceFingerprint']==voice['fingerprint'],'Current canonical voice differs from mixed source')
 levels=read(folder/'line-levels.json');draft=read(PROJECT/'narration-draft.json');tasks,all_tasks=context_tasks(voice,levels,build['mixWav'],draft)
 rp=Path(review_path).resolve();require(rp.is_relative_to((folder/'review/mixed-asr-v1').resolve()),'Original full-mix ASR proof must remain under this exact mix')
 job=read(rp.parent/'job.json');bp=baseline_review(rp,job,build,voice,all_tasks)
 require(job['identity']['lineLevelsSHA256']==sha(folder/'line-levels.json'),'Baseline accepted line-level artifact changed')
 pins=[pin(path),pin(folder/'input-recipe.json'),pin(folder/'line-levels.json'),pin(full.audio.VOICE),pin(PROJECT/'narration-draft.json'),bp,pin(rp.parent/'job.json')]+[pin(p)for p in [Path(__file__),HERE/'run-zen-view-mix-asr.py',HERE/'prepare-zen-view-audio.py',HERE/'run-selected-voice-qa.py',HERE/'run-first-asr.py',qa.TRUSTED,qa.GUARD]]
 identity=dict(protocol=PROTOCOL,adapterSHA256=sha(__file__),profile=PROFILE,audioBuildFingerprint=build['fingerprint'],voiceFingerprint=voice['fingerprint'],mix=build['mixWav'],tasks=tasks,modelPins=qa.APPROVED['modelPins'],trustedUtilitySHA256=qa.APPROVED['trustedSHA256'],baselineReview=bp,sourcePins=pins)
 return dict(identity=identity,preparationFingerprint=digest(identity),audioBuildPath=str(path),baselineReviewPath=str(rp),modelPath=str(qa.MODEL),metadataOnly=True,actualContextPcmHashed=False)

def make_job(audio_path,review_path):
 prepared=prepare_metadata(audio_path,review_path);identity=copy.deepcopy(prepared['identity'])
 for t in identity['tasks']:
  _,hashes=full.read_window(identity['mix'],t);t.update(hashes)
 fp=digest(identity);out=Path(audio_path).resolve().parent/'review/mixed-context-asr-v1'/fp[:24]
 return dict(protocol=PROTOCOL,fingerprint=fp,identity=identity,output=str(out),audioBuildPath=prepared['audioBuildPath'],baselineReviewPath=prepared['baselineReviewPath'],modelPath=str(qa.MODEL),fullActualMixCoverage=False,modelLoaded=False,expectedPrompt=None,hotwords=None,aliasesApplied=False,humanListening=False)

def recognition_record(job,task,result):
 words,flags=raw.words_from_raw(result,task)
 return dict(fingerprint=job['fingerprint'],task=task,text=result['text'],rawRecognition=copy.deepcopy(result),rawRecognitionSHA256=digest(result),globalWords=words,boundaryFlags=flags,comparison=raw.comparison(task['expected'],result['text']),expectedTextUse='comparison metadata only',expectedPrompt=None,hotwords=None,aliasesApplied=False,pcmModified=False,inputKind=PROFILE['inputKind'],stereoDownmix=PROFILE['stereoDownmix'],mixSHA256=job['identity']['mix']['sha256'],slicePcmSHA256=task['slicePcmSHA256'],monoPcmSHA256=task['monoPcmSHA256'],device='cuda',recognizer=str(qa.MODEL),fullActualMixCoverage=False,rawVoiceAsrReused=False,originalNarrowRecognitionReused=False,automaticSpeechPass=False,humanListening=False)

def cached(job,task):
 p=Path(job['output'])/(task['key']+'.json')
 if not p.exists():return None
 saved=read(p);require(saved==recognition_record(job,task,saved['rawRecognition']),'Contextual recognition cache changed');return saved

def cache_key(job,task):
 return digest(dict(profile=PROFILE,modelPins=job['identity']['modelPins'],trustedUtilitySHA256=job['identity']['trustedUtilitySHA256'],mixSHA256=task['audioSHA256'],beginSample=task['beginSample'],endSample=task['endSample'],slicePcmSHA256=task['slicePcmSHA256'],monoPcmSHA256=task['monoPcmSHA256']))
def cache_path(job,task):return Path(job['audioBuildPath']).parent/'review/blind-mixed-context-cache-v1'/(cache_key(job,task)+'.json')

def restore_cache(job):
 for t in job['identity']['tasks']:
  if cached(job,t)is not None:continue
  p=cache_path(job,t)
  if not p.exists():continue
  r=read(p);require(r['key']==cache_key(job,t)and r['profile']==PROFILE and r['modelPins']==job['identity']['modelPins']and r['trustedUtilitySHA256']==job['identity']['trustedUtilitySHA256']and digest(r['rawRecognition'])==r['rawRecognitionSHA256'],'Context-only cache input/model differs')
  origin=Path(r['originJob']['path']).resolve();allowed=(Path(job['audioBuildPath']).parent/'review/mixed-context-asr-v1').resolve()
  require(origin.is_relative_to(allowed)and sha(origin)==r['originJob']['sha256'],'Context cache origin is not preserved in exact selected mix')
  old=read(origin);require(old['identity']['profile']==PROFILE and old['identity']['modelPins']==job['identity']['modelPins']and old['identity']['trustedUtilitySHA256']==job['identity']['trustedUtilitySHA256']and old['identity']['mix']==job['identity']['mix']and sha(origin.parent/'adapter-source.py')==old['identity']['adapterSHA256'],'Context cache origin adapter/profile/model/input changed')
  require(len([previous for previous in old['identity']['tasks']if cache_key(old,previous)==cache_key(job,t)])==1,'Context cache has no exact same-input origin task')
  qa.voice.immutable_json(Path(job['output'])/(t['key']+'.json'),recognition_record(job,t,r['rawRecognition']))

def summary(job):
 records=[cached(job,t)for t in job['identity']['tasks']]
 if any(r is None for r in records):return None
 require(len(records)==2 and [r['task']['paragraphIndex']for r in records]==[5,7],'Only P5/P7 contextual results may complete')
 result=dict(status='two-contextual-paragraphs-complete-literal-and-hearing-review-pending',topicId='07.04',fingerprint=job['fingerprint'],audioBuildFingerprint=job['identity']['audioBuildFingerprint'],voiceFingerprint=job['identity']['voiceFingerprint'],mixSHA256=job['identity']['mix']['sha256'],contexts=records,contextCount=2,contextParagraphs=[5,7],sampleRate=48000,coveredContextSamples=sum(t['endSample']-t['beginSample']for t in job['identity']['tasks']),wholeMixFrames=job['identity']['mix']['frames'],fullActualMixCoverage=False,baselineNarrowReviewPreserved=job['identity']['baselineReview'],baselineResultsReplaced=False,rawRecognitionReusedAsMix=False,expectedPrompt=None,hotwords=None,aliasesApplied=False,pcmModified=False,automaticSpeechPass=False,humanListening=False,finalApproval=False)
 qa.voice.immutable_json(Path(job['output'])/'review.json',result);return result

def recognize(job_path,decline):
 path=Path(job_path).resolve();job=read(path);fresh=make_job(job['audioBuildPath'],job['baselineReviewPath'])
 require(path==Path(job['output'])/'job.json'and job==fresh,'Exact current contextual ASR job changed')
 for p in job['identity']['sourcePins']:require(sha(p['path'])==p['sha256'],'Context input/source/guard changed')
 for p in qa.APPROVED['modelPins']:require(sha(qa.MODEL/p['path'])==p['sha256'],'Approved recognizer model/tokenizer changed')
 restore_cache(job);pending=[t for t in job['identity']['tasks']if cached(job,t)is None]
 if not pending:return 0
 try:
  authorize()
  reason=qa.resource_reason()
  if reason:raise raw.PreModelResourceDeclined(reason,'complete-context-child-resource-check')
  os.environ.update(OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
  sys.path.insert(0,str(ROOT/'qwen3-tts'));guard=module('zen_context_approved_existing_guard',qa.GUARD);raw.acquire_guard_before_model(guard)
 except raw.PreModelResourceDeclined as e:
  p=Path(decline).resolve();require(p.parent==path.parent and p.name.startswith('resource-decline-'),'Invalid owned context decline path')
  save(p,dict(protocol=PROTOCOL,fingerprint=job['fingerprint'],phase='before-model',modelLoaded=False,temporary=True,reason=str(e),origin=e.origin));return 75
 trusted=module('zen_context_approved_blind_recognizer',qa.TRUSTED);require(trusted.MODEL==qa.MODEL,'Approved recognizer location changed')
 recognizer=trusted.load_recognizer('cuda')
 for t in pending:
  mono,hashes=full.read_window(job['identity']['mix'],t);require(all(t[k]==v for k,v in hashes.items()),'Actual complete paragraph PCM changed')
  result=trusted.recognize(recognizer,mono,48000) # Expected text never enters recognition.
  qa.voice.immutable_json(cache_path(job,t),dict(key=cache_key(job,t),profile=PROFILE,modelPins=job['identity']['modelPins'],trustedUtilitySHA256=job['identity']['trustedUtilitySHA256'],rawRecognition=result,rawRecognitionSHA256=digest(result),originJob=pin(path)))
  qa.voice.immutable_json(path.parent/(t['key']+'.json'),recognition_record(job,t,result));print('Recognized complete mixed paragraph',t['paragraphIndex'],flush=True)
 require(make_job(job['audioBuildPath'],job['baselineReviewPath'])['fingerprint']==job['fingerprint'],'Context inputs changed during recognition');return 0

def children():
 found=[]
 for p in psutil.process_iter(['cmdline']):
  try:
   args=p.info['cmdline']or[]
   if p.pid!=os.getpid()and'--recognize'in args and any(Path(a).name==Path(__file__).name for a in args):found.append(runtime.identity(p.pid))
  except psutil.NoSuchProcess:continue
  except psutil.AccessDenied:raise raw.Pending('Possible context child cannot be inspected')
 return found

def owned_alive(record):
 if runtime.alive(record):return True
 if children():return True
 if not record or record.get('phase')!='launching-context-model':return False
 command=record.get('launchCommand')
 if not command:return True
 for p in psutil.process_iter(['cmdline']):
  try:
   if p.info['cmdline']is None or p.info['cmdline']==command:return True
  except psutil.NoSuchProcess:continue
  except psutil.AccessDenied:return True
 return False

def accept_exit(code,decline,job):
 if code==0:return
 if code==75 and Path(decline).is_file():
  r=read(decline)
  if r.get('protocol')==PROTOCOL and r.get('fingerprint')==job['fingerprint']and r.get('phase')=='before-model'and r.get('modelLoaded')is False and r.get('temporary')is True:raise raw.ResourceRetry(r)
 raise RuntimeError('Context recognizer failed; preserve logs/results, no automatic inference retry')

def execute(audio_path,review_path,hours):
 require(type(hours)in(int,float)and math.isfinite(hours)and 0<hours<=6,'Finite wait above0 and at most6h required')
 require(not children(),'Existing contextual recognizer remains active')
 worker=runtime.SingleWorker(WORKER,is_alive=owned_alive).acquire();worker.update(stage='two-complete-paragraph-contexts');child=None;state=dict(protocol=PROTOCOL,owner=OWNER,**runtime.identity(),child=None,completed=False,status='waiting-for-context-resources');deadline=time.monotonic()+hours*3600
 try:
  metadata=prepare_metadata(audio_path,review_path)
  while True:
   authorize();reason=qa.resource_reason()
   if reason:
    state.update(reason=reason,status='waiting-for-context-resources');save(STATE,state)
    if time.monotonic()>=deadline:raise raw.Pending('Finite context wait ended; foreign jobs preserved')
    time.sleep(10);continue
   job=make_job(audio_path,review_path);folder=Path(job['output']);folder.mkdir(parents=True,exist_ok=True);path=folder/'job.json';qa.voice.immutable_json(path,job);qa.voice.immutable(folder/'adapter-source.py',Path(__file__).read_bytes());restore_cache(job)
   if summary(job):break
   nonce=uuid.uuid4().hex[:10];log=folder/('recognition-'+nonce+'.log');decline=folder/('resource-decline-'+nonce+'.json');command=[str(qa.PYTHON),'-B','-u','-X','utf8',str(Path(__file__)),'--recognize','--job',str(path),'--resource-decline',str(decline)]
   worker.update(phase='launching-context-model',launchCommand=command,child=None)
   with log.open('wb')as handle:
    child=subprocess.Popen(command,stdout=handle,stderr=subprocess.STDOUT,creationflags=CREATE);cid=runtime.identity(child.pid);worker.update(child=cid,phase='context-model-running');state.update(status='two-contexts-recognizing',child=cid,job=str(path),fingerprint=job['fingerprint']);save(STATE,state)
    while child.poll()is None:
     if time.monotonic()>=deadline:raise raw.Pending('Finite context wrapper ended with live child; preserve worker and child')
     time.sleep(5)
    code=child.returncode
   worker.update(child=None,phase='context-child-exited');state['child']=None
   try:accept_exit(code,decline,job)
   except raw.ResourceRetry as e:
    if time.monotonic()>=deadline:raise raw.Pending('Finite context pre-model retry ended')
    state.update(status='waiting-for-context-resources',reason=str(e));save(STATE,state);time.sleep(10);continue
   require(summary(job)is not None,'Context child finished without both paragraph results');break
  state.update(status='two-contexts-complete-literal-and-hearing-review-pending',completed=True,child=None,review=str(Path(job['output'])/'review.json'),fullActualMixCoverage=False,automaticSpeechPass=False,humanListening=False);save(STATE,state);return state
 except BaseException as e:
  state.update(status='context-wait-ended-or-failed-preserved',error=str(e),completed=False,child=runtime.identity(child.pid)if child and child.poll()is None else None);save(STATE,state);raise
 finally:worker.close(remove=not(child and child.poll()is None)and not children())

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--audio-build');p.add_argument('--baseline-review');p.add_argument('--execute',action='store_true');p.add_argument('--wait-hours',type=float,default=6);p.add_argument('--recognize',action='store_true');p.add_argument('--job');p.add_argument('--resource-decline');a=p.parse_args()
 if a.recognize:return recognize(a.job,a.resource_decline)
 if not a.audio_build or not a.baseline_review:
  require(not a.execute,'Exact accepted mix and original complete narrow-window review required');print(json.dumps(dict(ready=False,reason='Exact audio-build + baseline full-mix review required',modelLoaded=False,mediaExtracted=False)));return 0
 if a.execute:print(json.dumps(execute(a.audio_build,a.baseline_review,a.wait_hours),ensure_ascii=False));return 0
 data=prepare_metadata(a.audio_build,a.baseline_review);print(json.dumps(dict(ready=True,preparationFingerprint=data['preparationFingerprint'],paragraphs=[5,7],windows=[dict(paragraph=t['paragraphIndex'],beginSample=t['beginSample'],endSample=t['endSample'],durationSeconds=t['durationSeconds'])for t in data['identity']['tasks']],actualContextPcmHashed=False,mediaExtracted=False,modelLoaded=False,fullActualMixCoverage=False),ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
