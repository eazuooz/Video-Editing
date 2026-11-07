"""Independent06.02 final-mix paragraph ASR; preparation only unless --execute.

Exact25 selected mixed paragraph windows cover every48k sample; joins add context.
Raw speech recognition is a prerequisite, never mixed/encoded-audio evidence.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,math,os,subprocess,sys,time,uuid
from pathlib import Path
import numpy as np
import soundfile as sf
import psutil
from initialize import ROOT,HERE,MEDIA,read,save

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
QA_SHA='f190897764f2088fe8de425c622444a75ec6f5a4185763af5a02faa4a0caf4b1'
AUDIO_SHA='a7692cdc0ca3fdda1916afa553a66c2d8d925878fe25579b9d35821d6990b1da'
VERIFIER_SHA='db521babf1848861979a7580cd0a045540575f945909d99d2a7055433344f3b4'
if sha(HERE/'run-prospect-refuge-voice-qa-v2.py')!=QA_SHA or sha(HERE/'prepare-prospect-refuge-audio-v2.py')!=AUDIO_SHA:raise RuntimeError('Reviewed selected raw/audio source changed')
selected_qa=module('prospect_mixed_selected_raw_primitives',HERE/'run-prospect-refuge-voice-qa-v2.py');qa=selected_qa.qa
if sha(HERE/'verified-prospect-refuge-audio-build-v3.py')!=VERIFIER_SHA:raise RuntimeError('Reviewed read-only audio verifier changed')
audio=module('prospect_mixed_selected_audio_binding',HERE/'verified-prospect-refuge-audio-build-v3.py');producer=audio.producer
raw=qa.raw
PROTOCOL='architectural111-06-02-mix-asr-v1';OWNER='architectural-111-06-02-mix-asr'
runtime=module('zen_mixed_private_singleton',HERE/'run-first-native.py');runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER
TOPIC=MEDIA/'shorts-leveldesign-06-02';STATE=MEDIA/'06-02-mix-asr-progress.json';WORKER=MEDIA/'06-02-mix-asr-worker.json'
PROFILE=dict(qa.PROFILE,inputKind='actual-normalized-plus-BGM-final-mix',stereoDownmix='arithmetic mean of actual48k left/right usingfloat64 thenfloat32',coverage='exact25 contiguous paragraph windows covering103physicalcomponents plus24 contextual paragraph joins; no omitted quiet lead/tail',inputSampleRate=48000)
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)

def coverage(voice,levels,mix):
 """103 exact scalar units remain mapped;25 whole paragraphs cover every mix sample."""
 scenes=voice['identity']['scenes'];count=len(scenes)
 if(mix['sampleRate'],mix['channels'],mix['subtype'],mix['frames'])!=(48000,2,'FLOAT',voice['aggregateWav']['frames']*2):raise ValueError('Exact48k stereoFLOAT mixed source required')
 if count!=103 or len({s['id']for s in scenes})!=count or levels.get('voiceFingerprint')!=voice['fingerprint']or levels.get('rawCanonical')!=voice['aggregateWav']or len(levels.get('components',[]))!=count or len(voice['sceneWavs'])!=count or len(voice['paragraphMapping'])!=count:raise ValueError('Line levels not bound to exact103 selected scene identity')
 if not levels.get('originalRawFilesUnchanged')or levels.get('wordBoundariesShifted')or levels.get('voiceOffsetSeconds')!=0 or levels.get('insertedSamples')!=0 or levels.get('trimmedSamples')!=0 or levels.get('voiceSpeed')!=1 or levels.get('compressorUsed')is not False or levels.get('voiceSideDuck')is not False:raise ValueError('Changed speech timing/processing is not eligible')
 position=0;parts=[];rows=levels['components']
 for row,chunk,mapping,scene in zip(rows,voice['sceneWavs'],voice['paragraphMapping'],scenes):
  a,b=row['destinationSampleRange'];n=chunk['frames'];paragraph=row['paragraph']
  if type(a)is not int or type(b)is not int or type(n)is not int or n<=0 or a!=position or b-a!=n or row['sourceSampleRange']!=[0,n]or row['sceneId']!=mapping['sceneId']or row['sceneId']!=scene['id']or row['text']!=mapping['canonicalText']or row['text']!=' '.join(scene['lines'])or paragraph!=mapping['paragraph']or row['rawTakeSHA256']!=chunk['sha256']or row['rawPcmSHA256']!=chunk['pcmSHA256']or row['prepared48kSampleRange']!=[a*2,b*2]:raise ValueError('Mixed component differs from accepted ordered source/PCM/sample identity')
  parts.append(dict(sceneId=row['sceneId'],paragraph=paragraph,rawSampleRange=[a,b],mixedSampleRange=[a*2,b*2],rawTakeSHA256=chunk['sha256'],rawPcmSHA256=chunk['pcmSHA256'],expected=row['text']));position=b
 if position!=voice['aggregateWav']['frames']:raise ValueError('Mixed physical sample coverage is incomplete')
 if list(dict.fromkeys(r['paragraph']for r in parts))!=list(range(1,26))or[r['paragraph']for r in parts]!=sorted(r['paragraph']for r in parts):raise ValueError('Mixed identity must cover exactly25 authored paragraphs in order')
 takes=[];rate=48000
 for n in range(1,26):
  group=[r for r in parts if r['paragraph']==n];a=group[0]['mixedSampleRange'][0];b=group[-1]['mixedSampleRange'][1];sid=f'paragraph-{n:03}'
  takes.append(dict(key='mix-'+sid,kind='take',sceneId=sid,paragraphIndex=n,sourcePhysicalSceneIds=[r['sceneId']for r in group],sourcePhysicalComponents=group,path=mix['path'],audioSHA256=mix['sha256'],beginSample=a,endSample=b,offsetSample=a,offsetSeconds=a/rate,durationSeconds=(b-a)/rate,expected=' '.join(r['expected']for r in group)))
 joins=[]
 for left,right in zip(takes,takes[1:]):
  k=right['beginSample'];a=max(0,k-4*rate);b=min(mix['frames'],k+4*rate)
  joins.append(dict(key='mix-join-'+left['sceneId']+'-'+right['sceneId'],kind='boundary',joinType='paragraph-boundary',path=mix['path'],audioSHA256=mix['sha256'],beginSample=a,endSample=b,boundarySample=k,offsetSeconds=a/rate,durationSeconds=(b-a)/rate,previousScene=left['sceneId'],nextScene=right['sceneId'],expectedContextOnly=dict(previousEnding=' '.join(left['expected'].split()[-8:]),nextBeginning=' '.join(right['expected'].split()[:8]))))
 return takes+joins


def window_pcm(stereo):
 if stereo.ndim!=2 or stereo.shape[1]!=2 or not len(stereo)or not np.isfinite(stereo).all():raise ValueError('Finite nonempty stereo mixed window required')
 values=np.asarray(stereo,dtype='<f4');mono=values.mean(axis=1,dtype=np.float64).astype('<f4')
 return mono,dict(slicePcmSHA256=hashlib.sha256(values.tobytes()).hexdigest(),monoPcmSHA256=hashlib.sha256(mono.tobytes()).hexdigest())

def read_window(mix,task,verify_file=True):
 if task['path']!=mix['path']or task['audioSHA256']!=mix['sha256']or type(task['beginSample'])is not int or type(task['endSample'])is not int or not 0<=task['beginSample']<task['endSample']<=mix['frames']:raise ValueError('Mixed task file/hash/sample scope differs')
 if verify_file and sha(mix['path'])!=mix['sha256']:raise ValueError('Actual mixed WAV changed')
 samples,rate=sf.read(mix['path'],start=task['beginSample'],stop=task['endSample'],dtype='float32',always_2d=True)
 if rate!=48000 or len(samples)!=task['endSample']-task['beginSample']:raise ValueError('Mixed window decode differs from exact source clock')
 return window_pcm(samples)


def approved_model_pins():
 # Same reviewed approval checks as selected raw prepare_job, without rebuilding205 raw tasks.
 if sha(qa.TRUSTED)!=qa.APPROVED['trustedSHA256']or sha(qa.GUARD)!=qa.APPROVED['guardSHA256']or sha(HERE/'run-first-asr.py')!=qa.APPROVED['firstAsrPrimitiveSHA256']:raise ValueError('Approved recognizer/guard/ASR primitive changed')
 pins=[dict(path=p.name,sha256=sha(p))for p in sorted(qa.MODEL.iterdir())if p.is_file()and(p.suffix=='.safetensors'or p.name.endswith('.json')or p.name in('merges.txt','vocab.json'))]
 if pins!=qa.APPROVED['modelPins']or raw.PROFILE!=qa.PROFILE:raise ValueError('Approved ASR model/tokenizer/profile differs')
 return pins


def prepare_job(path):
 path=Path(path).resolve()
 if path.name!='audio-build.json'or not path.is_relative_to((TOPIC/'audio-preparation-v2').resolve()):raise ValueError('Exact selected audio build required')
 build=audio.verified_audio_build(path);folder=path.parent
 if build.get('schemaVersion')!='06-02-audio-build-v1'or build.get('topicId')!='06.02'or Path(build['output']).resolve()!=folder:raise ValueError('Wrong selected audio build')
 voice=read(producer.VOICE);mix=build['mixWav']
 if voice['fingerprint']!=build['rawVoiceFingerprint']or voice['aggregateWav']!=build['rawVoice']:raise ValueError('Selected raw voice changed after accepted audio verification')
 if sha(mix['path'])!=mix['sha256']:raise ValueError('Actual mixed WAV changed')
 levels=read(folder/'line-levels.json');tasks=coverage(voice,levels,mix)
 for task in tasks:
  _,hashes=read_window(mix,task,verify_file=False);task.update(hashes)
 if sha(mix['path'])!=mix['sha256']:raise ValueError('Actual mixed WAV changed while hashing windows')
 modelpins=approved_model_pins()
 sourcepaths=[Path(__file__),HERE/'verified-prospect-refuge-audio-build-v3.py',HERE/'prepare-prospect-refuge-audio-v2.py',HERE/'run-prospect-refuge-voice-qa-v2.py',HERE/'run-selected-voice-qa.py',HERE/'run-first-asr.py',qa.TRUSTED,qa.GUARD]
 sources=[pin(p)for p in sourcepaths]
 identity=dict(protocol=PROTOCOL,adapterSHA256=sha(__file__),profile=PROFILE,componentCount=103,paragraphCount=25,takeWindowCount=25,boundaryWindowCount=24,audioBuildFingerprint=build['fingerprint'],audioBuildSHA256=sha(path),voiceFingerprint=voice['fingerprint'],aggregateRawSHA256=voice['aggregateWav']['sha256'],mix=mix,lineLevelsSHA256=sha(folder/'line-levels.json'),tasks=tasks,modelPins=modelpins,trustedUtilitySHA256=qa.APPROVED['trustedSHA256'],sourcePins=sources)
 fp=digest(identity)
 return dict(protocol=PROTOCOL,fingerprint=fp,identity=identity,output=str(folder/'review/mixed-asr-v1'/fp[:24]),audioBuildPath=str(path),modelPath=str(qa.MODEL),sourcePins=sources,rawVoiceAsr=build['rawVoiceAsr'],rawVoiceRecognitionReusedAsMix=False,normalizedVoiceStem=pin(folder/'narration-stem.wav'),musicStem=pin(folder/'music-stem.wav'),encodedAACChecked=False,expectedPrompt=None,hotwords=None,aliasesApplied=False,humanListening=False)


def recognition_record(job,task,result):
 record=qa.recognition_record(job,task,result)
 record.update(inputKind=PROFILE['inputKind'],mixSHA256=job['identity']['mix']['sha256'],slicePcmSHA256=task['slicePcmSHA256'],monoPcmSHA256=task['monoPcmSHA256'],rawRecognitionSHA256=digest(result),stereoDownmix=PROFILE['stereoDownmix'],rawVoiceAsrReused=False,normalizedStemRecognized=False,encodedAACChecked=False)
 return record

def cache_key(job,task):return digest(dict(profile=PROFILE,modelPins=job['identity']['modelPins'],trustedUtilitySHA256=job['identity']['trustedUtilitySHA256'],mixSHA256=task['audioSHA256'],slicePcmSHA256=task['slicePcmSHA256'],monoPcmSHA256=task['monoPcmSHA256'],durationSeconds=task['durationSeconds'],expectedComparisonOnly=task.get('expected')))
def cache_path(job,task):return Path(job['audioBuildPath']).parent/'review/blind-mixed-cache-v1'/(cache_key(job,task)+'.json')

def cached(job,task):
 p=Path(job['output'])/(task['key']+'.json')
 if not p.is_file():return None
 record=read(p)
 if record!=recognition_record(job,task,record['rawRecognition']):raise ValueError('Mixed task cache literal/PCM provenance changed')
 return record

def restore_cache(job):
 for task in job['identity']['tasks']:
  if cached(job,task)is not None:continue
  path=cache_path(job,task)
  if not path.is_file():continue
  saved=read(path)
  if saved['key']!=cache_key(job,task)or saved['profile']!=PROFILE or saved['modelPins']!=job['identity']['modelPins']or saved['trustedUtilitySHA256']!=job['identity']['trustedUtilitySHA256']or digest(saved['rawRecognition'])!=saved['rawRecognitionSHA256']:raise ValueError('Mixed-only raw recognition cache differs')
  origin=Path(saved['originJob']['path']).resolve();root=Path(job['audioBuildPath']).parent/'review/mixed-asr-v1'
  if not origin.is_relative_to(root.resolve())or sha(origin)!=saved['originJob']['sha256']:raise ValueError('Mixed cache origin job is not preserved')
  prior=read(origin);snapshot=origin.parent/'adapter-source.py'
  if sha(snapshot)!=prior['identity']['adapterSHA256']or prior['identity']['profile']!=PROFILE:raise ValueError('Mixed cache origin adapter/profile differs')
  qa.voice.immutable_json(Path(job['output'])/(task['key']+'.json'),recognition_record(job,task,saved['rawRecognition']))

def summary(job):
 records=[cached(job,t)for t in job['identity']['tasks']]
 if any(r is None for r in records):return None
 takes=[r for r in records if r['task']['kind']=='take'];joins=[r for r in records if r['task']['kind']=='boundary'];mix=job['identity']['mix']
 if job['identity']['componentCount']!=103 or len(takes)!=25 or len(joins)!=24 or[t['task']['paragraphIndex']for t in takes]!=list(range(1,26))or takes[0]['task']['beginSample']!=0 or takes[-1]['task']['endSample']!=mix['frames']or any(a['task']['endSample']!=b['task']['beginSample']for a,b in zip(takes,takes[1:])):raise ValueError('Actual mixed paragraph coverage missing or duplicated')
 physical=[p for r in takes for p in r['task']['sourcePhysicalComponents']]
 if len(physical)!=103 or len({p['sceneId']for p in physical})!=103:raise ValueError('Mixed physical component provenance incomplete')
 paragraphs=[dict(paragraph=r['task']['paragraphIndex'],sceneIds=r['task']['sourcePhysicalSceneIds'],expectedLiteral=r['task']['expected'],recognizedLiteral=r['text'],comparison=raw.comparison(r['task']['expected'],r['text']),globalWords=r['globalWords'],recognitionBasis='independent-actual-final-mix-full-paragraph-window',sourceResult=pin(Path(job['output'])/(r['task']['key']+'.json')))for r in takes]
 result=dict(status='mixed-asr-complete-literal-and-listening-review-pending',topicId='06.02',fingerprint=job['fingerprint'],audioBuildFingerprint=job['identity']['audioBuildFingerprint'],mixSHA256=mix['sha256'],mixedAudioPath=mix['path'],voiceFingerprint=job['identity']['voiceFingerprint'],sampleRate=48000,frames=mix['frames'],fullActualMixCoverage=True,coveredSamples=sum(t['task']['endSample']-t['task']['beginSample']for t in takes),physicalComponentCount=103,physicalComponentMapping=physical,takes=takes,paragraphs=paragraphs,boundaryWindows=joins,rawVoiceAsr=job['rawVoiceAsr'],rawVoiceRecognitionReusedAsMix=False,normalizedStemRecognized=False,encodedAACChecked=False,expectedPrompt=None,hotwords=None,aliasesApplied=False,pcmModified=False,automaticSpeechPass=False,humanListening=False,finalApproval=False)
 qa.voice.immutable_json(Path(job['output'])/'review.json',result);return result


def recognize(job_path,decline_path):
 path=Path(job_path).resolve();job=read(path);fresh=prepare_job(job['audioBuildPath'])
 if path!=Path(job['output'])/'job.json'or job['identity']!=fresh['identity']or digest(job['identity'])!=job['fingerprint']:raise ValueError('Actual selected mixed ASR job changed')
 for p in job['sourcePins']:
  if sha(p['path'])!=p['sha256']:raise ValueError('Mixed ASR source/guard changed')
 restore_cache(job);pending=[t for t in job['identity']['tasks']if cached(job,t)is None]
 if not pending:return 0
 try:
  reason=qa.resource_reason()
  if reason:raise raw.PreModelResourceDeclined(reason,'mixed-child-resource-check')
  os.environ.update(OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
  sys.path.insert(0,str(ROOT/'qwen3-tts'));guard=module('zen_mixed_existing_gpu_guard',qa.GUARD);raw.acquire_guard_before_model(guard)
 except raw.PreModelResourceDeclined as e:
  p=Path(decline_path).resolve()
  if p.parent!=path.parent or not p.name.startswith('resource-decline-'):raise ValueError('Invalid owned pre-model decline path')
  save(p,dict(protocol=PROTOCOL,fingerprint=job['fingerprint'],phase='before-model',modelLoaded=False,temporary=True,reason=str(e),origin=e.origin));return 75
 trusted=module('zen_mixed_trusted_recognizer',qa.TRUSTED)
 if trusted.MODEL!=qa.MODEL:raise ValueError('Approved mixed recognizer model differs')
 recognizer=trusted.load_recognizer('cuda')  # Actual model/inference failures are never resource retries.
 for task in pending:
  mono,hashes=read_window(job['identity']['mix'],task,verify_file=False)
  if any(task[k]!=v for k,v in hashes.items()):raise ValueError('Actual mixed task PCM changed before recognition')
  result=trusted.recognize(recognizer,mono,48000)  # No expected text, hotwords or prompt supplied.
  qa.voice.immutable_json(cache_path(job,task),dict(key=cache_key(job,task),profile=PROFILE,modelPins=job['identity']['modelPins'],trustedUtilitySHA256=job['identity']['trustedUtilitySHA256'],rawRecognition=result,rawRecognitionSHA256=digest(result),originJob=pin(path)))
  qa.voice.immutable_json(path.parent/(task['key']+'.json'),recognition_record(job,task,result));print('Recognized actual mixed window',task['key'],flush=True)
 if prepare_job(job['audioBuildPath'])['fingerprint']!=job['fingerprint']:raise ValueError('Mixed inputs changed during ASR')
 return 0

def accept_exit(code,decline,job):
 if code==0:return
 if code==75 and Path(decline).is_file():
  r=read(decline)
  if r.get('protocol')==PROTOCOL and r.get('fingerprint')==job['fingerprint']and r.get('phase')=='before-model'and r.get('modelLoaded')is False and r.get('temporary')is True:raise raw.ResourceRetry(r)
 raise RuntimeError('Mixed ASR child failed; preserve exact log. Actual model/recognition failures are not resource retries.')

def children():
 result=[]
 for p in psutil.process_iter(['cmdline']):
  try:
   args=p.info['cmdline']or[]
   if p.pid!=os.getpid()and'--recognize'in args and any(Path(a).name==Path(__file__).name for a in args):result.append(runtime.identity(p.pid))
  except psutil.NoSuchProcess:continue
  except psutil.AccessDenied:raise raw.Pending('Possible owned mixed recognizer cannot be inspected')
 return result

def execute(build_path,wait_hours):
 if not math.isfinite(wait_hours)or not 0<=wait_hours<=6:raise ValueError('Finite owned wait must be between0and6hours')
 if children():raise RuntimeError('Existing mixed recognizer preserved')
 worker=runtime.SingleWorker(WORKER).acquire();worker.update(stage='independent-mixed-ASR',topicId='06.02');child=None;state=dict(protocol=PROTOCOL,owner=OWNER,**runtime.identity(),child=None,status='waiting-for-resources',completed=False,modelLoadedByWrapper=False);deadline=time.monotonic()+max(0,wait_hours)*3600
 try:
  while True:
   job=prepare_job(build_path);folder=Path(job['output']);folder.mkdir(parents=True,exist_ok=True);path=folder/'job.json'
   qa.voice.immutable_json(path,job);qa.voice.immutable(folder/'adapter-source.py',Path(__file__).read_bytes());restore_cache(job)
   if summary(job):break
   reason=qa.resource_reason();state.update(status='waiting-for-resources',reason=reason,child=None,job=str(path),fingerprint=job['fingerprint']);save(STATE,state)
   if reason:
    if time.monotonic()>=deadline:raise raw.Pending('Finite mixed-ASR resource wait ended; foreign jobs/apps preserved')
    time.sleep(10);continue
   nonce=uuid.uuid4().hex[:10];log=folder/('recognition-'+nonce+'.log');decline=folder/('resource-decline-'+nonce+'.json')
   command=[str(qa.PYTHON),'-B','-u','-X','utf8',str(Path(__file__)),'--recognize','--job',str(path),'--resource-decline',str(decline)]
   with log.open('wb')as handle:
    child=subprocess.Popen(command,stdout=handle,stderr=subprocess.STDOUT,creationflags=CREATE);cid=runtime.identity(child.pid);worker.update(child=cid);state.update(child=cid,status='independent-mixed-ASR-running',log=str(log));save(STATE,state);code=child.wait()
   worker.update(child=None);state.update(child=None,childStillAlive=False)
   try:accept_exit(code,decline,job)
   except raw.ResourceRetry as e:
    state.update(status='waiting-for-resources',reason=str(e),lastResourceDecline=pin(decline));save(STATE,state)
    if time.monotonic()>=deadline:raise raw.Pending('Finite pre-model resource retry deadline ended')
    time.sleep(10);continue
   if not summary(job):raise RuntimeError('Mixed ASR child exited without all actual window results')
   break
  state.update(status='mixed-asr-complete-literal-review-pending',completed=True,child=None,review=str(Path(job['output'])/'review.json'),modelLoadedByWrapper=False,automaticSpeechPass=False,humanListening=False);save(STATE,state);return state
 except BaseException as error:
  state.update(status='mixed-ASR-failed-or-finite-wait-ended',error=str(error),completed=False,child=runtime.identity(child.pid)if child and child.poll()is None else None);save(STATE,state);raise
 finally:worker.close(remove=not(child and child.poll()is None))

def main():
 p=argparse.ArgumentParser();p.add_argument('--audio-build');p.add_argument('--execute',action='store_true');p.add_argument('--wait-hours',type=float,default=6);p.add_argument('--recognize',action='store_true');p.add_argument('--job');p.add_argument('--resource-decline');a=p.parse_args()
 if a.recognize:return recognize(a.job,a.resource_decline)
 if not a.audio_build:
  if a.execute:raise ValueError('Exact completed selected audio build required')
  print(json.dumps(dict(ready=False,reason='Exact completed06.02 audio-build.json required',modelLoaded=False)));return 0
 if a.execute:print(json.dumps(execute(a.audio_build,a.wait_hours),ensure_ascii=False));return 0
 try:
  job=prepare_job(a.audio_build);print(json.dumps(dict(ready=True,fingerprint=job['fingerprint'],takes=25,joins=24,physicalComponentCount=103,coveredSamples=job['identity']['mix']['frames'],modelLoaded=False,actualMixedPcmInspectedForHashOnly=True),ensure_ascii=False))
 except(FileNotFoundError,audio.Pending,raw.Pending)as e:print(json.dumps(dict(ready=False,reason=str(e),modelLoaded=False),ensure_ascii=False))
 return 0

if __name__=='__main__':raise SystemExit(main())
