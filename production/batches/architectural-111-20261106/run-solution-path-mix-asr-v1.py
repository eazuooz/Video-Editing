"""11.05 actual final-mix ASR:14 whole paragraphs +13 contextual joins.

Default has no job/model/resource side effects. Only root's explicit --execute
can run the unchanged approved blind recognizer and finite selected lifecycle.
Raw48take ASR is a prerequisite, never substituted for actual mixed recognition.
"""
from __future__ import annotations
import argparse, ast, copy, hashlib, importlib.util, json, math, os, re, sys, types
from pathlib import Path
import numpy as np
import soundfile as sf
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
TOPIC=MEDIA/'shorts-leveldesign-11-05';PROJECT=ROOT/'projects/shorts-leveldesign-11-05'
DEST=TOPIC/'audio-preparation-v5'
PROTOCOL='architectural111-11-05-mix-asr-v1';OWNER='architectural-111-11-05-mix-asr'
STATE=MEDIA/'11-05-mix-asr-v1-progress.json';WORKER=MEDIA/'11-05-mix-asr-v1-worker.json'
VOICE_FP='6691614beecda682a8130136a3dfd952b472e7acdba769a83cd1ca7212df8cc1'
REPAIR_FP='10b7ed1345e8075db6d4f0ee9bf706d52951f2a163fbd60c9d7d278b4d6a839a'
NARRATION=PROJECT/'narration-final-v5.json'
NARRATION_SHA='e3179da81b2a23135eb6a8907ebb6205c14fc2d66e528a37372d491d0ffeaa91'
PINS={
 'run-selected-voice-qa.py':'65983206f0e0fa81dd5a5780871605fcc2665816a9f21fc3ea3a43781437e2a9',
 'run-solution-path-voice-qa-v6.py':'59618eb71570190ec78cbae98f94b15078cfd852d3325aab7ac10531400d727e',
 'run-prospect-refuge-mix-asr.py':'566155e4164f6884366de2141fdfa480b84d1df39c65dd876836d8f97a9ff3db',
 'prepare-solution-path-audio-v6.py':'839c2a8f2fe2c996dc5c722d1f6427d5633e23b50a49dd31d5ff286af08bec05',
 'prepare-solution-path-audio-mix-v5.py':'1cfa0c387321c73d3b5442cd25ce1cbe144ea5b1573dc2f40498e887f5b62fc3',
 'verified-solution-path-audio-build-v5.py':'0c1d86561745ceca1260a137c57dba0231546a5cf7a1ae547f5b6eb37132a55b'}
SELF_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

class Pending(RuntimeError):pass
def need(value,reason):
 if not value:raise Pending(reason)
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def pin(path):return dict(path=str(Path(path).resolve()),sha256=sha(path))
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value);return value
def check_sources():
 need(sha(__file__)==SELF_SHA,'Mixed-ASR source changed after import')
 for name,value in PINS.items():need(value is not None and sha(HERE/name)==value,'Reviewed mixed-ASR dependency missing/changed: '+name)
 need(sha(NARRATION)==NARRATION_SHA,'Current NarV5 source changed')
check_sources()
qa=module('solution_mixed_private_selected_lifecycle',HERE/'run-selected-voice-qa.py')
raw_adapter=module('solution_mixed_current_raw6',HERE/'run-solution-path-voice-qa-v6.py')
audio=module('solution_mixed_current_build5',HERE/'verified-solution-path-audio-build-v5.py')
qa.voice=raw_adapter.qa.voice;raw=qa.raw
PROFILE=dict(qa.PROFILE,inputKind='actual-normalized-plus-BGM-final-mix',
 stereoDownmix='arithmetic mean of actual48k left/right usingfloat64 thenfloat32',
 coverage='exact14 contiguous whole-paragraph windows covering every selected raw component and mixed sample plus13 contextual paragraph joins; natural lead/tail retained',inputSampleRate=48000)
CURRENT_BUILD=None
RESOURCE=raw_adapter.resource
LAUNCHER_RUNTIME_PINS=copy.deepcopy(raw_adapter.LAUNCHER_RUNTIME_PINS)
_process_reason=raw_adapter._process_reason
_base_resource_reason=qa.resource_reason

def raw_worker_barrier():
 try:raw_adapter.legacy_barrier()
 except raw_adapter.Pending as error:raise Pending(str(error))from error
 for name in ('11-05-asr-v6-progress.json','11-05-asr-v6-worker.json'):
  path=MEDIA/name
  if not path.exists():continue
  try:value=read(path)
  except(OSError,ValueError):raise Pending('Uninspected rawV6 worker preserved')
  need(isinstance(value,dict) and not qa.voice.alive(value) and not qa.voice.alive(value.get('child')),
       'RawV6 coordinator/child still live or uninspected; preserve it')
 for process in qa.psutil.process_iter(['pid','name','cmdline']):
  try:
   args=process.info['cmdline']
   if args is None:
    need(not(process.info.get('name')or'').lower().startswith('python'),'Unknown possible raw recognizer preserved')
   elif '--recognize' in args and any(Path(a).name=='run-solution-path-voice-qa-v6.py' for a in args):
    raise Pending('Unregistered rawV6 recognizer preserved')
  except qa.psutil.NoSuchProcess:continue
  except qa.psutil.AccessDenied:raise Pending('Possible raw recognizer cannot be inspected')

def coverage(voice,levels,mix,paragraph_texts=None):
 scenes=voice['identity']['scenes'];count=len(scenes);rows=levels.get('components',[])
 need(count>0 and len({s['id']for s in scenes})==count and levels.get('schemaVersion')=='11.05-line-levels-v5'
      and levels.get('componentCount')==count and levels.get('rawCanonical')==voice['aggregateWav']
      and len(rows)==len(voice['sceneWavs'])==len(voice['paragraphMapping'])==count,'Exact current component lineage required')
 need((mix['sampleRate'],mix['channels'],mix['subtype'],mix['frames'])==(48000,2,'FLOAT',voice['aggregateWav']['frames']*2),'Exact2x stereoFLOAT mixed grid required')
 need(all(levels.get(k)==v for k,v in dict(voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,voiceSpeed=1.,wordBoundariesShifted=False).items()),'Changed voice timing is not eligible')
 position=0;parts=[]
 for scene,row,wav,mapping in zip(scenes,rows,voice['sceneWavs'],voice['paragraphMapping']):
  a,b=row['destinationSampleRange'];n=wav['frames']
  need(type(a)is type(b)is type(n)is int and n>0 and a==position and b-a==n
       and row['sourceSampleRange']==[0,n] and row['prepared48kSampleRange']==[2*a,2*b]
       and row['sceneId']==mapping['sceneId']==scene['id'] and row['text']==mapping['canonicalText']==' '.join(scene['lines'])
       and row['paragraph']==mapping['paragraph'] and row['rawTakeSHA256']==wav['sha256'] and row['rawPcmSHA256']==wav['pcmSHA256'],
       'Mixed component order/text/PCM/sample lineage differs')
  parts.append(dict(sceneId=scene['id'],paragraph=row['paragraph'],rawSampleRange=[a,b],mixedSampleRange=[2*a,2*b],
                    rawTakeSHA256=wav['sha256'],rawPcmSHA256=wav['pcmSHA256'],expected=row['text']));position=b
 need(position==voice['aggregateWav']['frames'] and list(dict.fromkeys(r['paragraph']for r in parts))==list(range(1,15))
      and [r['paragraph']for r in parts]==sorted(r['paragraph']for r in parts),'Exact14 paragraphs must cover all raw/mixed samples in order')
 takes=[]
 for n in range(1,15):
  group=[r for r in parts if r['paragraph']==n];a=group[0]['mixedSampleRange'][0];b=group[-1]['mixedSampleRange'][1];sid=f'paragraph-{n:03}'
  text=' '.join(r['expected']for r in group)
  need(paragraph_texts is None or text==paragraph_texts[n-1],'Mixed paragraph text differs from current narration')
  takes.append(dict(key='mix-'+sid,kind='take',sceneId=sid,paragraphIndex=n,sourcePhysicalSceneIds=[r['sceneId']for r in group],sourcePhysicalComponents=group,
       path=mix['path'],audioSHA256=mix['sha256'],beginSample=a,endSample=b,offsetSample=a,offsetSeconds=a/48000,durationSeconds=(b-a)/48000,expected=text))
 joins=[]
 for left,right in zip(takes,takes[1:]):
  boundary=right['beginSample'];a=max(0,boundary-4*48000);b=min(mix['frames'],boundary+4*48000)
  joins.append(dict(key='mix-join-'+left['sceneId']+'-'+right['sceneId'],kind='boundary',joinType='paragraph-boundary',path=mix['path'],audioSHA256=mix['sha256'],
       beginSample=a,endSample=b,boundarySample=boundary,offsetSample=a,offsetSeconds=a/48000,durationSeconds=(b-a)/48000,
       previousScene=left['sceneId'],nextScene=right['sceneId'],expectedContextOnly=dict(previousEnding=' '.join(left['expected'].split()[-8:]),nextBeginning=' '.join(right['expected'].split()[:8]))))
 return takes+joins

# Reuse only neutral, previously exercised mixed-window/recognizer/cache bodies.
# No old06 wrapper,103/25 scope, controller or path constants are imported.
PRIMITIVES=('window_pcm','read_window','approved_model_pins','recognition_record','cache_key','cache_path','cached','restore_cache','recognize')
tree=ast.parse((HERE/'run-prospect-refuge-mix-asr.py').read_text(encoding='utf-8-sig'))
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in PRIMITIVES]
need({n.name for n in nodes}==set(PRIMITIVES),'Exact pinned mixed primitive set missing')
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(HERE/'run-prospect-refuge-mix-asr.py'),'exec'),globals())
save=qa.save
_restore_mixed_primitive=restore_cache

def restore_cache(job):
 # Recognition stays within this exact actual mix/model/audited adapter. The
 # immutable rawV6 caches and another mix/output are never migration sources.
 root=(Path(job['audioBuildPath']).parent/'review/mixed-asr-v1').resolve()
 for task in job['identity']['tasks']:
  if cached(job,task)is not None:continue
  cache=cache_path(job,task)
  if not cache.is_file():continue
  saved=read(cache);origin=Path(saved['originJob']['path']).resolve()
  need(origin.is_relative_to(root) and origin.is_file() and pin(origin)==saved['originJob'],'Mixed cache origin escaped actual build')
  prior=read(origin);identity=prior['identity']
  need(prior.get('protocol')==PROTOCOL and digest(identity)==prior['fingerprint']
       and identity.get('adapterSHA256')==SELF_SHA and sha(origin.parent/'adapter-source.py')==SELF_SHA
       and all(identity.get(k)==job['identity'][k]for k in('profile','modelPins','trustedUtilitySHA256','mix','audioBuildFingerprint')),
       'Mixed cache origin model/source/input identity differs')
  need(any(cache_key(prior,t)==cache_key(job,task)for t in identity['tasks']),'Mixed cache is not a real matching source window')
 return _restore_mixed_primitive(job)

def verified_raw_review(voice,timing,record):
 path=Path(record['path']).resolve();need(pin(path)==record,'Raw ASR review pin changed')
 review=read(path);job_path=path.parent/'job.json';job=read(job_path)
 need(path.name=='review.json' and path.parent==Path(job['output']).resolve() and job.get('protocol')==raw_adapter.PROTOCOL
      and job['identity']['voiceFingerprint']==voice['fingerprint'] and job['voiceEvidence']==pin(Path(voice['output'])/'voice-complete-proof.json')
      and job['identity']['sourceNarration']==pin(NARRATION) and job['identity']['profile']==raw_adapter.PROFILE
      and job['identity']['modelPins']==qa.APPROVED['modelPins'] and job['identity']['trustedUtilitySHA256']==qa.APPROVED['trustedSHA256']
      and job['identity']['adapterSHA256']==PINS['run-solution-path-voice-qa-v6.py'] and digest(job['identity'])==job['fingerprint'],
      'Raw ASR belongs to different source/voice/model/job')
 need(sha(path.parent/'adapter-source.py')==PINS['run-solution-path-voice-qa-v6.py'],'Raw ASR actual adapter snapshot differs')
 for row in job['sourcePins']:need(pin(row['path'])==row,'Raw ASR source pin changed')
 need(job['identity']['tasks']==raw_adapter.qa.build_tasks(voice,timing),'Raw95 task sample envelopes differ')
 need(all(raw_adapter.cached(job,t)is not None for t in job['identity']['tasks']),'Actual raw ASR cache incomplete')
 def existing(destination,value):need(Path(destination).resolve()==path and value==review,'Raw ASR summary differs from exact caches')
 fn=raw_adapter.summary;scope=dict(fn.__globals__,voice=types.SimpleNamespace(immutable_json=existing))
 rebuilt=types.FunctionType(fn.__code__,scope,'read_only_current_raw_summary')(job)
 need(rebuilt==review and len(review['takes'])==len(voice['identity']['scenes']) and len(review['boundaryWindows'])==len(voice['identity']['scenes'])-1
      and len(review['paragraphs'])==14 and review['voiceFingerprint']==voice['fingerprint'] and review['aggregateSHA256']==voice['aggregateWav']['sha256']
      and review['timingSHA256']==voice['timing']['sha256'] and review['aliasesApplied'] is False and review['expectedPrompt'] is None
      and review['automaticSpeechPass'] is False,'Current full raw-ASR prerequisite differs')
 return review,pin(job_path)

def prepare_job(path=None):
 check_sources();raw_worker_barrier()
 path=Path(path or CURRENT_BUILD or '').resolve()
 need(path.name=='audio-build.json' and path.is_file() and path.parent.parent==DEST.resolve()
      and re.fullmatch('[0-9a-f]{24}',path.parent.name) is not None,'Exact completed current audio-build.json is pending')
 try:build=audio.verified_audio_build(path);out,voice,timing,draft=raw_adapter.exact_voice()
 except(audio.Pending,raw_adapter.Pending)as error:raise Pending(str(error))from error
 need(build['schemaVersion']=='11.05-audio-build-v5' and build['topicId']=='11.05' and Path(build['output']).resolve()==path.parent
      and build['rawVoiceFingerprint']==VOICE_FP==voice['fingerprint'] and voice['repairFingerprint']==REPAIR_FP
      and build['rawVoice']==voice['aggregateWav'] and build['canonicalTiming']==voice['timing'],'Current repaired accepted mix binding differs')
 _,raw_job_pin=verified_raw_review(voice,timing,build['rawVoiceAsr'])
 mix=build['mixWav'];levels=read(path.parent/'line-levels.json');tasks=coverage(voice,levels,mix,draft['narrationKo'])
 need(sha(mix['path'])==mix['sha256'],'Actual mixed source changed')
 for task in tasks:
  _,hashes=read_window(mix,task,verify_file=False);task.update(hashes)
 need(sha(mix['path'])==mix['sha256'],'Mixed source changed while hashing its windows')
 modelpins=approved_model_pins()
 sources=[pin(__file__)]+[pin(HERE/name)for name in PINS]+[pin(NARRATION),raw_job_pin,pin(path),build['rawVoiceAsr'],build['rawNumericalLevelReview'],build['acceptedComponentsReview'],pin(qa.TRUSTED),pin(qa.GUARD)]+copy.deepcopy(LAUNCHER_RUNTIME_PINS)
 sources=list({r['path']:r for r in sources}.values())
 identity=dict(protocol=PROTOCOL,adapterSHA256=SELF_SHA,profile=PROFILE,componentCount=len(voice['identity']['scenes']),paragraphCount=14,takeWindowCount=14,boundaryWindowCount=13,
       audioBuildFingerprint=build['fingerprint'],audioBuildSHA256=sha(path),voiceFingerprint=voice['fingerprint'],repairFingerprint=voice['repairFingerprint'],
       aggregateRawSHA256=voice['aggregateWav']['sha256'],mix=mix,lineLevelsSHA256=sha(path.parent/'line-levels.json'),tasks=tasks,modelPins=modelpins,
       trustedUtilitySHA256=qa.APPROVED['trustedSHA256'],sourceNarration=pin(NARRATION),sourcePins=sources)
 fp=digest(identity)
 return dict(protocol=PROTOCOL,fingerprint=fp,identity=identity,output=str(path.parent/'review/mixed-asr-v1'/fp[:24]),audioBuildPath=str(path),modelPath=str(qa.MODEL),sourcePins=sources,
       rawVoiceAsr=build['rawVoiceAsr'],rawVoiceRecognitionReusedAsMix=False,normalizedVoiceStem=pin(path.parent/'narration-stem.wav'),musicStem=pin(path.parent/'music-stem.wav'),
       encodedAACChecked=False,expectedPrompt=None,hotwords=None,aliasesApplied=False,humanListening=False)

def summary(job):
 records=[cached(job,t)for t in job['identity']['tasks']]
 if any(r is None for r in records):return None
 takes=[r for r in records if r['task']['kind']=='take'];joins=[r for r in records if r['task']['kind']=='boundary'];mix=job['identity']['mix'];count=job['identity']['componentCount']
 need(len(takes)==14 and len(joins)==13 and [r['task']['paragraphIndex']for r in takes]==list(range(1,15))
      and takes[0]['task']['beginSample']==0 and takes[-1]['task']['endSample']==mix['frames']
      and all(a['task']['endSample']==b['task']['beginSample']for a,b in zip(takes,takes[1:])),'Actual whole-mix paragraph coverage incomplete')
 physical=[p for r in takes for p in r['task']['sourcePhysicalComponents']]
 need(len(physical)==count and len({r['sceneId']for r in physical})==count,'Physical component provenance incomplete')
 paragraphs=[dict(paragraph=r['task']['paragraphIndex'],sceneIds=r['task']['sourcePhysicalSceneIds'],expectedLiteral=r['task']['expected'],recognizedLiteral=r['text'],
       comparison=raw.comparison(r['task']['expected'],r['text']),globalWords=r['globalWords'],recognitionBasis='independent-actual-final-mix-full-paragraph-window',
       sourceResult=pin(Path(job['output'])/(r['task']['key']+'.json')))for r in takes]
 result=dict(schemaVersion='11.05-mixed-asr-review-v1',status='mixed-asr-complete-literal-and-listening-review-pending',topicId='11.05',fingerprint=job['fingerprint'],
       audioBuildFingerprint=job['identity']['audioBuildFingerprint'],mixSHA256=mix['sha256'],mixedAudioPath=mix['path'],voiceFingerprint=job['identity']['voiceFingerprint'],
       sampleRate=48000,frames=mix['frames'],fullActualMixCoverage=True,coveredSamples=sum(r['task']['endSample']-r['task']['beginSample']for r in takes),
       physicalComponentCount=count,physicalComponentMapping=physical,takes=takes,paragraphs=paragraphs,boundaryWindows=joins,rawVoiceAsr=job['rawVoiceAsr'],
       rawVoiceRecognitionReusedAsMix=False,normalizedStemRecognized=False,encodedAACChecked=False,expectedPrompt=None,hotwords=None,aliasesApplied=False,
       pcmModified=False,automaticSpeechPass=False,humanListening=False,finalApproval=False)
 qa.voice.immutable_json(Path(job['output'])/'review.json',result);return result

# Keep the reviewed direct Dvenv -> Cbase matcher, changing ONLY the exact mixed
# job root and review-folder component. All runtime/argv/PID/ctime checks remain.
node=next(n for n in ast.parse((HERE/'run-solution-path-voice-qa-v6.py').read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef)and n.name=='launcher_matches')
source=ast.get_source_segment((HERE/'run-solution-path-voice-qa-v6.py').read_text(encoding='utf-8'),node)
source=source.replace("(ROOT / 'shared/output/architectural-111-20261106/11-05/voice-attempts').resolve()","DEST.resolve()")
source=source.replace("('review', 'independent-asr-selected-v1')","('review', 'mixed-asr-v1')")
exec(compile(source,str(Path(__file__).resolve()),'exec'),globals())

def scoped_process_reason(info,own_pid,qualified=frozenset()):
 if os.name=='nt' and info.get('pid')==os.getppid():
  try:
   fields=['pid','ppid','create_time','name','exe','cmdline'];own=qa.psutil.Process(os.getpid()).as_dict(fields);parent=qa.psutil.Process(own['ppid']).as_dict(fields)
   if launcher_matches(info,own,parent):return None
  except(qa.psutil.NoSuchProcess,qa.psutil.AccessDenied):pass
 return _process_reason(info,own_pid,qualified)

def resource_reason():
 check_sources();raw_adapter.check_sources();return _base_resource_reason()

def children():
 names={'run-solution-path-voice-qa-v4.py','run-solution-path-voice-qa-v5.py','run-solution-path-voice-qa-v6.py',Path(__file__).name,
        'run-selected-voice-qa.py','run-first-asr.py','run-prospect-refuge-mix-asr.py','run-zen-view-mix-asr.py'}
 result=[]
 for p in qa.psutil.process_iter(['pid','name','cmdline']):
  try:
   args=p.info['cmdline']
   if args is None:
    need(not(p.info.get('name')or'').lower().startswith('python'),'Uninspected possible recognizer preserved')
   elif p.pid!=os.getpid() and '--recognize' in args and any(Path(a).name in names for a in args):result.append(qa.voice.identity(p.pid))
  except qa.psutil.NoSuchProcess:continue
  except qa.psutil.AccessDenied:raise Pending('Possible recognizer cannot be inspected')
 return result

RESOURCE.process_reason=scoped_process_reason
qa.PROTOCOL,qa.OWNER,qa.SLUG,qa.TOPIC=PROTOCOL,OWNER,'shorts-leveldesign-11-05','11.05'
qa.STATE,qa.WORKER=STATE,WORKER
qa.Pending=Pending
qa.raw.SLUG=qa.SLUG;qa.runtime.PROTOCOL,qa.runtime.OWNER=PROTOCOL,OWNER
qa.__file__=str(Path(__file__).resolve())
qa.prepare_job,qa.restore_raw_cache,qa.cached,qa.summary=prepare_job,restore_cache,cached,summary
qa.recognize,qa.child_processes,qa.resource_reason=recognize,children,resource_reason

def main(argv=None):
 global CURRENT_BUILD
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--audio-build');parser.add_argument('--execute',action='store_true');parser.add_argument('--wait-hours',type=float,default=6)
 parser.add_argument('--recognize',action='store_true');parser.add_argument('--job');parser.add_argument('--resource-decline');args=parser.parse_args(argv)
 if args.recognize:
  need(args.job and args.resource_decline,'Exact mixed child job/decline paths required')
  return recognize(args.job,args.resource_decline)
 if not args.audio_build:
  need(not args.execute,'Exact accepted current audio-build is required')
  print(json.dumps(dict(ready=False,reason='Actual current accepted mixed audio-build is pending',modelLoaded=False,jobLaunched=False)));return 0
 CURRENT_BUILD=Path(args.audio_build).resolve()
 try:
  if args.execute:
   need(math.isfinite(args.wait_hours)and 0<args.wait_hours<=6,'Finite wait must be above0 and at most6 hours')
   qa.execute(args.wait_hours);return 0
  job=prepare_job(CURRENT_BUILD);print(json.dumps(dict(ready=True,fingerprint=job['fingerprint'],takes=14,joins=13,componentCount=job['identity']['componentCount'],coveredSamples=job['identity']['mix']['frames'],modelLoaded=False,jobLaunched=False)))
 except(Pending,audio.Pending,raw_adapter.Pending,FileNotFoundError)as error:
  print(json.dumps(dict(ready=False,reason=str(error),modelLoaded=False,jobLaunched=False)))
  if args.execute:raise SystemExit(2)
 return 0

if __name__=='__main__':raise SystemExit(main())
