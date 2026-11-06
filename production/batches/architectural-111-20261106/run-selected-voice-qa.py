"""Selected07.04 blind word ASR and separate raw-PCM level/join review.

Default preflight is read-only. --execute runs the finite ASR controller; --levels
runs CPU numerical review only after exact ASR caches are complete. No TTS, audio
editing, AAC decoding, caption acceptance, automatic speech pass or human hearing.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,math,os,subprocess,sys,time,uuid,wave
from fractions import Fraction
from pathlib import Path
sys.dont_write_bytecode=True
import psutil
from initialize import ROOT,HERE,MEDIA,AUTH_KEY,read,save

APPROVED={'model': 'C:\\Users\\1\\.cache\\huggingface\\hub\\models--openai--whisper-large-v3-turbo\\snapshots\\41f01f3fe87f28c78e2fbf8b568835947dd65ed9', 'modelPins': [{'path': 'added_tokens.json', 'sha256': '3c51f66c4c21f9e126970078f11ae77a78c74aee8df606ee9daba86e467108e0'}, {'path': 'config.json', 'sha256': 'c5b526b3e3cd64cd8940dabb45e8ba726629e22d8ed389c29b552f9140daf04a'}, {'path': 'generation_config.json', 'sha256': 'cce11bfe3aaa6ae9e072ea2637caaec8795e68d9b67e655a5af16ee509681a4c'}, {'path': 'merges.txt', 'sha256': '2df2990a395e35e8dfbc7511e08c12d56018d8d04691e0133e5d63b21e154dc6'}, {'path': 'model.safetensors', 'sha256': '542566a422ae4f3fd23f1ba11add198fca01bbf82e66e6a2857b3f608b1eb9d1'}, {'path': 'normalizer.json', 'sha256': 'bf1c507dc8724ca9cf9903640dacfb69dae2f00edee4f21ceba106a7392f26dd'}, {'path': 'preprocessor_config.json', 'sha256': '7ccc62c6f2765af1f3b46c00c9b5894426835a05021c8b9c01eecb6dfb542711'}, {'path': 'special_tokens_map.json', 'sha256': 'baea4ea09372eb4fca86b4e4346139fd73cb807d5087e9de0948e971739c3e74'}, {'path': 'tokenizer.json', 'sha256': '297b13372ac43916285644fb9687add3cc62ee2a1adb60da3dc25cc94c1871fd'}, {'path': 'tokenizer_config.json', 'sha256': '844b642c73a91359722f47b35705f7174686df33d252695d8572cf9ac03a6389'}, {'path': 'vocab.json', 'sha256': 'e2aa043ef015641d363d8288e7c241c85e36a5c761fb303598e0710233344387'}], 'trusted': 'production/batches/game-math-remaining-20261104/review-source-voice.py', 'trustedSHA256': 'c20e3b12aa06f8ee252b83151be3ae39753a7a5e5a74e080415bca6b0c65c855', 'guard': 'qwen3-tts/gpu_handoff_guard.py', 'guardSHA256': 'ee57e07c73d932e8bdb993a61334478331d675e03039c03d58a08d95d473bb48', 'firstAsrPrimitiveSHA256': '7e38f2565fcf44b45ff6a94c68c7a359a497515c28ed462c729a36c7d1e6864e', 'firstLevelPrimitiveSHA256': '545104df16cf26af0c0637faa76750bea1e5b70f424cc13820f13baa8b773544', 'profile': {'model': 'whisper-large-v3-turbo', 'device': 'cuda', 'dtype': 'float16', 'attention': 'eager', 'minimumFreeMiB': 9216, 'allocationCapGiB': 7, 'language': 'korean', 'task': 'transcribe', 'timestamps': 'word', 'chunkLengthSeconds': 28, 'strideLengthSeconds': 4, 'boundaryRadiusSeconds': 4, 'expectedPrompt': None, 'hotwords': None, 'aliases': None}, 'pinSource': {'path': 'shared/output/architectural-111-20261106/03-02/voice-v1/review/independent-asr-v1/5408e628e0e7a569ad7b1c32/job.json', 'sha256': '1a8ce3faee2b987bc6f0b4201171f1e156aec909a5da39acc7cbda725fe6d649'}}
PROFILE=APPROVED['profile'];MODEL=Path(APPROVED['model']);TRUSTED=ROOT/APPROVED['trusted'];GUARD=ROOT/APPROVED['guard']
SLUG='shorts-leveldesign-07-04';TOPIC='07.04';PROTOCOL='architectural111-selected-voice-asr-v1';OWNER='architectural-111-07-04-asr'
PROOF=MEDIA/'07-04-voice-evidence.json';VOICE_STATE=MEDIA/'07-04-voice-progress.json';STATE=MEDIA/'07-04-asr-progress.json';WORKER=MEDIA/'07-04-asr-worker.json';PYTHON=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
voice=module('selected_qa_voice_tools',HERE/'run-selected-voice.py')
raw=module('selected_qa_first_pure_asr',HERE/'run-first-asr.py');raw.SLUG=SLUG
runtime=module('selected_qa_singleton_runtime',HERE/'run-first-native.py');runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER
class Pending(RuntimeError):pass

def sha(path):return voice.sha(path)
def digest(x):return raw.digest(x)
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def pcm_bytes(path,start=0,end=None):
 with wave.open(str(path),'rb') as w:
  if w.getparams().nchannels!=1 or w.getparams().sampwidth!=2 or w.getframerate()!=24000:raise ValueError('Exact24k mono PCM16 required')
  end=w.getnframes() if end is None else end
  if not 0<=start<end<=w.getnframes():raise ValueError('Invalid half-open PCM window')
  w.setpos(start);data=w.readframes(end-start)
  if len(data)!=(end-start)*2:raise ValueError('Truncated PCM window')
  return data

def exact_voice():
 control=read(ROOT/'shared/publishing/video-production-control.json')[AUTH_KEY]
 if control['status'] in ('paused','stopped','cancelled') or not control['automaticAdvanceWithinExactList'] or control['automaticAdvanceOutsideList'] or not control['humanFinalReviewRequired']:raise Pending('Selected finite batch authorization is not active')
 if not PROOF.is_file() or not VOICE_STATE.is_file():raise Pending('Waiting for exact completed07.04 voice evidence')
 proof=read(PROOF);state=read(VOICE_STATE)
 if not state.get('completed') or voice.alive(state.get('child')) or voice.project_children(SLUG):raise Pending('Selected Qwen voice child/evidence is still active')
 out=Path(proof['output']).resolve();expected=(ROOT/'shared/output/architectural-111-20261106/07-04/voice-attempts').resolve()
 if out.parent!=expected or out.name!=proof['fingerprint'][:24] or state.get('fingerprint')!=proof['fingerprint']:raise ValueError('Wrong selected voice/output identity')
 identity=proof['identity']
 if digest(identity)!=proof['fingerprint']:raise ValueError('Voice synthesis identity hash differs')
 current=voice.verify_complete(dict(fingerprint=proof['fingerprint'],identity=identity),out)
 if current is None or any(current[k]!=proof[k] for k in ['sceneWavs','aggregateWav','timing','paragraphMapping']):raise ValueError('Canonical complete voice proof differs')
 draft=read(ROOT/'projects'/SLUG/'narration-draft.json');mapping=proof['paragraphMapping'];scenes=identity['scenes'];byid={s['id']:s for s in scenes}
 if len(byid)!=len(scenes) or [m['sceneId'] for m in mapping]!=[s['id'] for s in scenes]:raise ValueError('Take/paragraph mapping is missing or reordered')
 groups={}
 for row in mapping:groups.setdefault(row['paragraph'],[]).append(' '.join(byid[row['sceneId']]['lines']))
 if list(groups)!=list(range(1,len(draft['narrationKo'])+1)) or [' '.join(v) for v in groups.values()]!=draft['narrationKo']:raise ValueError('Current authored paragraphs differ from selected spoken PCM')
 timing=read(proof['timing']['path']);entries=timing['entries'];position=0;pcm=hashlib.sha256()
 if len(entries)!=len(scenes) or len(proof['sceneWavs'])!=len(scenes):raise ValueError('Variable take count differs')
 for s,e,w in zip(scenes,entries,proof['sceneWavs']):
  if Path(w['path']).resolve()!=out/'chunks'/f'{s["id"]}-scene.wav' or e['scene_id']!=s['id'] or e['text']!=' '.join(s['lines']):raise ValueError('Exact raw scene/time/text binding differs')
  if abs(e['start']-position/24000)>1/24000 or abs(e['end']-(position+w['frames'])/24000)>1/24000:raise ValueError('Canonical take sample boundary differs')
  pcm.update(pcm_bytes(w['path']));position+=w['frames']
 if position!=proof['aggregateWav']['frames'] or pcm.hexdigest()!=proof['aggregateWav']['pcmSHA256']:raise ValueError('Canonical aggregate is not exact selected raw concatenation')
 return out,proof,timing,draft

def build_tasks(proof,timing):
 takes=[];joins=[];rate=24000;position=0;mapping={r['sceneId']:r['paragraph'] for r in proof['paragraphMapping']}
 for entry,chunk in zip(timing['entries'],proof['sceneWavs']):
  sid=entry['scene_id'];take=dict(key='take-'+sid,kind='take',sceneId=sid,paragraphIndex=mapping[sid],path=chunk['path'],audioSHA256=chunk['sha256'],pcmIdentity={k:chunk[k] for k in ['sha256','pcmSHA256','sampleRate','channels','sampleWidthBytes','frames']},offsetSample=position,endSample=position+chunk['frames'],offsetSeconds=position/rate,durationSeconds=chunk['frames']/rate,expected=entry['text'])
  takes.append(take);position+=chunk['frames']
 for left,right in zip(takes,takes[1:]):
  boundary=right['offsetSample'];a=max(0,boundary-4*rate);b=min(position,boundary+4*rate);data=pcm_bytes(proof['aggregateWav']['path'],a,b)
  joins.append(dict(key='join-'+left['sceneId']+'-'+right['sceneId'],kind='boundary',joinType='internal-component' if left['paragraphIndex']==right['paragraphIndex'] else 'paragraph-boundary',path=proof['aggregateWav']['path'],audioSHA256=proof['aggregateWav']['sha256'],slicePcmSHA256=hashlib.sha256(data).hexdigest(),beginSample=a,endSample=b,boundarySample=boundary,offsetSample=a,offsetSeconds=a/rate,durationSeconds=(b-a)/rate,previousScene=left['sceneId'],nextScene=right['sceneId'],previousParagraph=left['paragraphIndex'],nextParagraph=right['paragraphIndex'],expectedContextOnly=dict(previousEnding=' '.join(left['expected'].split()[-8:]),nextBeginning=' '.join(right['expected'].split()[:8]))))
 return takes+joins

def prepare_job():
 out,proof,timing,draft=exact_voice()
 if sha(TRUSTED)!=APPROVED['trustedSHA256'] or sha(GUARD)!=APPROVED['guardSHA256'] or sha(HERE/'run-first-asr.py')!=APPROVED['firstAsrPrimitiveSHA256']:raise ValueError('Approved recognizer/guard/ASR primitive changed')
 modelpins=[dict(path=p.name,sha256=sha(p)) for p in sorted(MODEL.iterdir()) if p.is_file() and (p.suffix=='.safetensors' or p.name.endswith('.json') or p.name in ('merges.txt','vocab.json'))]
 if modelpins!=APPROVED['modelPins'] or raw.PROFILE!=PROFILE:raise ValueError('Approved ASR model/tokenizer/profile differs')
 identity=dict(protocol=PROTOCOL,adapterSHA256=sha(Path(__file__)),voiceVerifierSHA256=sha(HERE/'run-selected-voice.py'),voiceFingerprint=proof['fingerprint'],aggregateSHA256=proof['aggregateWav']['sha256'],aggregatePcmSHA256=proof['aggregateWav']['pcmSHA256'],timingSHA256=proof['timing']['sha256'],modelPins=modelpins,trustedUtilitySHA256=APPROVED['trustedSHA256'],profile=PROFILE,tasks=build_tasks(proof,timing))
 fp=digest(identity);folder=out/'review/independent-asr-selected-v1'/fp[:24]
 return dict(protocol=PROTOCOL,fingerprint=fp,identity=identity,output=str(folder),voiceOutput=str(out),voiceEvidence=pin(PROOF),modelPath=str(MODEL),sourcePins=[pin(Path(__file__)),pin(HERE/'run-selected-voice.py'),pin(HERE/'run-first-asr.py'),pin(TRUSTED),pin(GUARD)],humanListening=False,pcmModified=False,finalApproval=False)

def recognition_record(job,task,result):
 words,flags=raw.words_from_raw(result,task)
 for i,w in enumerate(words):w.update(sourceSceneId=task.get('sceneId'),sourceWordIndex=i)
 compare=raw.comparison(task['expected'],result['text']) if task['kind']=='take' else dict(expectedContextOnly=task['expectedContextOnly'],recognizedLiteral=result['text'],warning='Window edges may cut words; no automatic missing-word verdict or PCM trimming.',automaticSpeechPass=False)
 return dict(fingerprint=job['fingerprint'],task=task,text=result['text'],rawRecognition=copy.deepcopy(result),globalWords=words,boundaryFlags=flags,comparison=compare,expectedPrompt=None,aliasesApplied=False,pcmModified=False,device='cuda',recognizer=str(MODEL),humanListening=False)

def cache_key(job,task):
 # Only this selected voice output; no cross-project/archive search.
 return digest(dict(profile=PROFILE,modelPins=job['identity']['modelPins'],trustedUtilitySHA256=job['identity']['trustedUtilitySHA256'],audioSHA256=task['audioSHA256'],slicePcmSHA256=task.get('slicePcmSHA256'),pcmIdentity=task.get('pcmIdentity'),expectedLiteral=task.get('expected'),durationSeconds=task['durationSeconds']))
def raw_cache_path(job,task):return Path(job['voiceOutput'])/'review/blind-raw-cache-v1'/(cache_key(job,task)+'.json')
def cached(job,task):
 p=Path(job['output'])/(task['key']+'.json')
 if not p.is_file():return None
 record=read(p)
 if record!=recognition_record(job,task,record['rawRecognition']):raise ValueError('ASR literal/raw/timestamp cache changed')
 return record

def restore_raw_cache(job):
 count=0
 for task in job['identity']['tasks']:
  if cached(job,task) is not None:continue
  p=raw_cache_path(job,task)
  if not p.is_file():continue
  data=read(p)
  if data['key']!=cache_key(job,task) or data['modelPins']!=job['identity']['modelPins'] or data['profile']!=PROFILE or data['trustedUtilitySHA256']!=job['identity']['trustedUtilitySHA256']:raise ValueError('Blind raw recognition provenance differs')
  if data['rawRecognitionSHA256']!=digest(data['rawRecognition']):raise ValueError('Raw recognition cache changed')
  origin=Path(data['originJob']['path']).resolve();voice_root=Path(job['voiceOutput']).resolve()
  if not origin.is_relative_to(voice_root/'review/independent-asr-selected-v1') or sha(origin)!=data['originJob']['sha256']:raise ValueError('Raw cache origin job missing or changed')
  prior=read(origin)
  if prior['identity']['profile']!=PROFILE or prior['identity']['trustedUtilitySHA256']!=job['identity']['trustedUtilitySHA256'] or prior['identity']['modelPins']!=job['identity']['modelPins']:raise ValueError('Raw cache origin recognizer differs')
  source=origin.parent/'adapter-source.py'
  if sha(source)!=prior['identity']['adapterSHA256']:raise ValueError('Raw cache origin adapter source missing or changed')
  voice.immutable_json(Path(job['output'])/(task['key']+'.json'),recognition_record(job,task,data['rawRecognition']));count+=1
 return count

def summary(job):
 records=[cached(job,t) for t in job['identity']['tasks']]
 if any(r is None for r in records):return None
 takes=[r for r in records if r['task']['kind']=='take'];joins=[r for r in records if r['task']['kind']=='boundary'];paragraphs=[];boundaries=[]
 for n in sorted({r['task']['paragraphIndex'] for r in takes}):
  group=[r for r in takes if r['task']['paragraphIndex']==n];expected=' '.join(r['task']['expected'] for r in group);recognized=' '.join(r['text'].strip() for r in group)
  paragraphs.append(dict(paragraph=n,sceneIds=[r['task']['sceneId'] for r in group],startSample=group[0]['task']['offsetSample'],endSample=group[-1]['task']['endSample'],start=group[0]['task']['offsetSample']/24000,end=group[-1]['task']['endSample']/24000,expectedLiteral=expected,recognizedLiteral=recognized,comparison=raw.comparison(expected,recognized),globalWords=[w for r in group for w in r['globalWords']],recognitionBasis='assembled-from-blind-component-takes',sourceResults=[dict(path=str(Path(job['output'])/(r['task']['key']+'.json')),sha256=sha(Path(job['output'])/(r['task']['key']+'.json'))) for r in group]))
 for left,right,window in zip(takes,takes[1:],joins):
  last=[w for w in left['globalWords'] if w['timestamp'][1] is not None];first=[w for w in right['globalWords'] if w['timestamp'][0] is not None]
  boundaries.append(dict(previousScene=left['task']['sceneId'],nextScene=right['task']['sceneId'],joinType=window['task']['joinType'],boundarySample=window['task']['boundarySample'],recognizedWordGapSeconds=None if not last or not first else first[0]['timestamp'][0]-last[-1]['timestamp'][1],interpretation='Timing observation only; original natural lead/tail retained. No silence-trim or hearing approval.'))
 result=dict(status='independent-asr-complete-content-review-pending',fingerprint=job['fingerprint'],voiceFingerprint=job['identity']['voiceFingerprint'],aggregateSHA256=job['identity']['aggregateSHA256'],timingSHA256=job['identity']['timingSHA256'],profile=PROFILE,takes=takes,paragraphs=paragraphs,boundaryWindows=joins,boundaryObservations=boundaries,aliasesApplied=False,expectedPrompt=None,automaticSpeechPass=False,humanListening=False,pcmModified=False,encodedAacChecked=False,finalApproval=False)
 voice.immutable_json(Path(job['output'])/'review.json',result);return result

def resource_reason():
 reason=voice.busy_reason()
 if reason:return reason
 rawgpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=CREATE);free,use=map(int,rawgpu.splitlines()[0].replace(' ','').split(','))
 return 'Approved ASR requires9216MiB free and utilization below15%' if free<9216 or use>=15 else None

def recognize(job_path,decline):
 job_path=Path(job_path).resolve();job=read(job_path);fresh=prepare_job()
 if job_path.name!='job.json' or job_path.parent!=Path(job['output']).resolve() or job['output']!=fresh['output'] or job['voiceOutput']!=fresh['voiceOutput'] or job['identity']!=fresh['identity'] or digest(job['identity'])!=job['fingerprint']:raise ValueError('Selected exact ASR job changed')
 for p in job['sourcePins']:
  if sha(p['path'])!=p['sha256']:raise ValueError('Pinned ASR helper/recognizer source changed')
 restore_raw_cache(job);pending=[t for t in job['identity']['tasks'] if cached(job,t) is None]
 if not pending:return
 try:
  reason=resource_reason()
  if reason:raise raw.PreModelResourceDeclined(reason,'selected-child-resource-check')
  os.environ.update(OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
  sys.path.insert(0,str(ROOT/'qwen3-tts'));guard=module('selected_qa_existing_gpu_guard',GUARD);raw.acquire_guard_before_model(guard)
 except raw.PreModelResourceDeclined as e:
  p=Path(decline).resolve()
  if p.parent!=job_path.parent or not p.name.startswith('resource-decline-'):raise ValueError('Invalid pre-model-decline path')
  save(p,dict(protocol=PROTOCOL,fingerprint=job['fingerprint'],phase='before-model',modelLoaded=False,temporary=True,reason=str(e),origin=e.origin));return 75
 trusted=module('selected_qa_trusted_blind_recognizer',TRUSTED)
 if trusted.MODEL!=MODEL:raise ValueError('Trusted recognizer model location differs')
 recognizer=trusted.load_recognizer('cuda')
 import numpy as np
 for task in pending:
  if sha(task['path'])!=task['audioSHA256']:raise ValueError('Exact audio file changed before recognition')
  data=pcm_bytes(task['path'],task.get('beginSample',0),task.get('endSample') if task['kind']=='boundary' else None)
  if task.get('slicePcmSHA256') and hashlib.sha256(data).hexdigest()!=task['slicePcmSHA256']:raise ValueError('Exact join slice changed')
  samples=np.frombuffer(data,dtype='<i2').astype(np.float32)/32768.;result=trusted.recognize(recognizer,samples,24000)
  record=recognition_record(job,task,result)
  voice.immutable_json(raw_cache_path(job,task),dict(key=cache_key(job,task),profile=PROFILE,modelPins=job['identity']['modelPins'],trustedUtilitySHA256=job['identity']['trustedUtilitySHA256'],rawRecognition=result,rawRecognitionSHA256=digest(result),originJob=pin(job_path)))
  voice.immutable_json(Path(job['output'])/(task['key']+'.json'),record);print('Recognized',task['key'],flush=True)
 if prepare_job()['fingerprint']!=job['fingerprint']:raise ValueError('Exact voice/ASR inputs changed during recognition')
 return 0

def raw_level_review(job_path):
 job_path=Path(job_path).resolve();job=read(job_path);fresh=prepare_job()
 if job_path!=Path(fresh['output'])/'job.json' or job['output']!=fresh['output'] or job['identity']!=fresh['identity']:raise ValueError('Level review requires current exact voice/ASR inputs')
 review=summary(job)
 if review is None:raise Pending('Complete exact take and join ASR caches required for word-level review')
 if sha(HERE/'first-level-continuity-review.py')!=APPROVED['firstLevelPrimitiveSHA256']:raise ValueError('Approved numerical level primitives changed')
 mathqa=module('selected_qa_raw_level_primitives',HERE/'first-level-continuity-review.py')
 import numpy as np
 takes=[];allwords={};flags=[]
 for recognized in review['takes']:
  task=recognized['task'];samples=np.frombuffer(pcm_bytes(task['path']),dtype='<i2').astype(np.float32)/32768.;words=[];invalid=[]
  for i,word in enumerate(recognized['rawRecognition'].get('chunks',[])):
   stamp=word['timestamp']
   if any(t is None or not isinstance(t,(int,float)) or not math.isfinite(t) for t in stamp):invalid.append(dict(index=i,text=word['text'],timestamp=stamp,reason='unknown/nonfinite-word-boundary'));continue
   if stamp[0]<0 or stamp[1]<=stamp[0]:invalid.append(dict(index=i,text=word['text'],timestamp=stamp,reason='non-increasing-word-window'));continue
   a,b=mathqa.sample_window(stamp[0],stamp[1],24000)
   if a<0 or b>len(samples)+1 or b<=a:invalid.append(dict(index=i,text=word['text'],timestamp=stamp,reason='word-window-outside-exact-take'));continue
   a=max(0,a);b=min(len(samples),b)
   if b<=a:continue
   words.append(dict(recognizedText=word['text'],startSeconds=(task['offsetSample']+a)/24000,endSeconds=(task['offsetSample']+b)/24000,durationSeconds=(b-a)/24000,globalRawSampleRange=[task['offsetSample']+a,task['offsetSample']+b],levels={'canonical':mathqa.levels(samples[a:b],24000)}))
  stats=mathqa.trend(words,'canonical');row=dict(sceneId=task['sceneId'],paragraph=task['paragraphIndex'],levels=mathqa.levels(samples,24000),wordTrend=stats,wordRecords=words,invalidWordWindows=invalid);takes.append(row);allwords[task['sceneId']]=words
  if stats['suspect']:flags.append(dict(kind='sustained-take-word-body-decline',sceneId=task['sceneId'],trend=stats))
  if invalid:flags.append(dict(kind='incomplete-word-level-measurement',sceneId=task['sceneId'],windows=invalid))
 paragraphs=[]
 for para in review['paragraphs']:
  words=[w for sid in para['sceneIds'] for w in allwords[sid]];stats=mathqa.trend(words,'canonical');paragraphs.append(dict(paragraph=para['paragraph'],sceneIds=para['sceneIds'],wordTrend=stats))
  if stats['suspect']:flags.append(dict(kind='sustained-paragraph-word-body-decline',paragraph=para['paragraph'],trend=stats))
 finite=[p['wordTrend'].get('medianBodyDbfs') for p in paragraphs if p['wordTrend'].get('medianBodyDbfs') is not None]
 if finite:
  median=float(np.median(finite))
  for paragraph in paragraphs:
   value=paragraph['wordTrend'].get('medianBodyDbfs')
   if value is not None and value-median<=mathqa.POLICY['paragraphBelowMedianWarningDb']:flags.append(dict(kind='paragraph-word-body-below-other-paragraphs',paragraph=paragraph['paragraph'],deltaDb=value-median,comparisonMedianDbfs=median,interpretation='Numerical review target; different words/emphasis may differ. No gain or pass inferred.'))
 out,proof,_,_=exact_voice();rawpcm=np.frombuffer(pcm_bytes(proof['aggregateWav']['path']),dtype='<i2').astype(np.float32)/32768.;joins=[]
 for observed in review['boundaryObservations']:
  k=observed['boundarySample'];left=rawpcm[max(0,k-240):k];right=rawpcm[k:min(len(rawpcm),k+240)]
  joins.append(dict(**observed,rawLeftLastSample=float(rawpcm[k-1]),rawRightFirstSample=float(rawpcm[k]),absoluteSampleJump=float(abs(rawpcm[k]-rawpcm[k-1])),left10ms=mathqa.levels(left,24000),right10ms=mathqa.levels(right,24000),interpretationScope='Numerical sample/word-gap observation only; no click/hearing/continuity acceptance is inferred.'))
 result=dict(status='raw-PCM-numerical-level-and-join-review-complete-listening-pending',asrReview=pin(Path(job['output'])/'review.json'),voiceFingerprint=proof['fingerprint'],canonicalWav=proof['aggregateWav'],policy=mathqa.POLICY,levelPrimitive=pin(HERE/'first-level-continuity-review.py'),takes=takes,paragraphs=paragraphs,joins=joins,flags=flags,pcmModified=False,actualListening=False,automaticSpeechPass=False,normalizationApplied=False,encodedAacChecked=False,preparedMixOrMusicChecked=False,humanApproval=False)
 fp=digest(dict(asr=result['asrReview'],canonicalSHA256=proof['aggregateWav']['sha256'],primitive=result['levelPrimitive'],policy=result['policy']));dest=Path(job['output'])/'raw-level-review'/fp[:24]/'review.json';voice.immutable_json(dest,result);return dest

def child_processes():
 out=[]
 for p in psutil.process_iter(['pid','cmdline']):
  try:
   args=p.info['cmdline'] or []
   if p.pid!=os.getpid() and '--recognize' in args and any(Path(a).name=='run-selected-voice-qa.py' for a in args):out.append(voice.identity(p.pid))
  except psutil.NoSuchProcess:continue
  except psutil.AccessDenied:raise Pending('Possible recognizer child cannot be inspected; preserve it')
 return out

def execute(wait_hours):
 if child_processes():raise RuntimeError('Existing selected recognizer child preserved')
 worker=runtime.SingleWorker(WORKER,is_alive=voice.alive).acquire();worker.update(**voice.identity(),stage='independent-ASR',topicId=TOPIC)
 child=None;log=None;state=dict(protocol=PROTOCOL,owner=OWNER,**voice.identity(),child=None,status='waiting-for-exact-voice',completed=False,modelLoadedByWrapper=False,engineOwnsGpuLease=True);deadline=time.monotonic()+wait_hours*3600
 try:
  while True:
   try:
    if time.monotonic()>=deadline:raise RuntimeError('Finite ASR wait ended; foreign jobs preserved')
    job=prepare_job();folder=Path(job['output']);voice.immutable_json(folder/'job.json',job);voice.immutable(folder/'adapter-source.py',Path(__file__).read_bytes());restore_raw_cache(job)
    if summary(job):break
    if (folder/'failed-asr.json').exists():raise RuntimeError('Prior model/recognition failure preserved; inspect before retry')
    reason=resource_reason()
    if reason:raise Pending(reason)
    if child_processes():raise Pending('Existing recognizer child must finish')
    if prepare_job()['fingerprint']!=job['fingerprint']:continue
    ident=uuid.uuid4().hex[:8];log_path=folder/('recognition-'+ident+'.log');decline=folder/('resource-decline-'+ident+'.json');log=log_path.open('ab')
    command=[str(PYTHON),'-u','-X','utf8',str(Path(__file__).resolve()),'--recognize','--job',str(folder/'job.json'),'--resource-decline',str(decline)]
    worker.update(phase='launching',command=command,job=str(folder/'job.json'));child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=CREATE);childid=voice.identity(child.pid);worker.update(child=childid,phase='running');state.update(status='independent-ASR-running',child=childid,job=str(folder/'job.json'),log=str(log_path));save(STATE,state)
    while child.poll() is None:
     if time.monotonic()>=deadline:raise Pending('Finite wrapper wait ended with recognizer child alive; preserve it')
     time.sleep(5)
    code=child.returncode;log.close();log=None
    if code==75:
     decline_record=read(decline)
     if decline_record.get('protocol')!=PROTOCOL or decline_record.get('fingerprint')!=job['fingerprint'] or decline_record.get('modelLoaded') is not False or decline_record.get('phase')!='before-model':raise RuntimeError('Invalid pre-model resource-decline receipt')
     worker.update(child=None);state['child']=None;child=None;raise Pending(decline_record['reason'])
    if code:
     voice.immutable_json(folder/'failed-asr.json',dict(exitCode=code,log=pin(log_path),fingerprint=job['fingerprint'],modelFailureNotResourceRetry=True))
     raise RuntimeError('ASR model/recognition child failed; preserve caches/log and stop')
    if prepare_job()['fingerprint']!=job['fingerprint'] or summary(job) is None:raise RuntimeError('ASR output/input completeness differs')
    break
   except Pending as e:
    state.update(status='waiting-for-resources-or-exact-voice',reason=str(e),checkedAt=time.time());save(STATE,state)
    if (child and child.poll() is None) or time.monotonic()>=deadline:break
    time.sleep(10)
  state.update(completed=bool('job' in locals() and summary(job)),status='independent-asr-complete-content-review-pending' if 'job' in locals() and summary(job) else 'finite-wait-ended',review=str(Path(job['output'])/'review.json') if 'job' in locals() else None,humanListening=False,automaticSpeechPass=False)
 except BaseException as e:state.update(status='failed-preserved',error=repr(e),completed=False);raise
 finally:
  live=bool(child and child.poll() is None) or bool(child_processes());state.update(childStillAlive=live,finishedOrYieldedAt=time.time())
  if live:state['status']='yielded-recognizer-child-still-alive'
  save(STATE,state)
  if log:log.close()
  worker.close(remove=not live)
 print(json.dumps(state,ensure_ascii=False))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true');ap.add_argument('--wait-hours',type=float,default=6);ap.add_argument('--recognize',action='store_true');ap.add_argument('--job');ap.add_argument('--resource-decline');ap.add_argument('--levels',action='store_true');args=ap.parse_args()
 if args.recognize:
  if not args.job or not args.resource_decline:raise ValueError('Child needs exact job and resource-decline path')
  raise SystemExit(recognize(args.job,args.resource_decline))
 if args.levels:
  if not args.job or args.execute:raise ValueError('CPU levels requires one exact --job and no model execution flag')
  print(str(raw_level_review(args.job)));return
 if args.execute:
  if not math.isfinite(args.wait_hours) or not 0<args.wait_hours<=6:raise ValueError('Finite wait must be0..6hours')
  execute(args.wait_hours);return
 try:
  job=prepare_job();print(json.dumps(dict(ready=True,asrFingerprint=job['fingerprint'],takeCount=sum(t['kind']=='take' for t in job['identity']['tasks']),joinCount=sum(t['kind']=='boundary' for t in job['identity']['tasks']),modelLoaded=False,staged=False),ensure_ascii=False))
 except Pending as e:print(json.dumps(dict(ready=False,reason=str(e),modelLoaded=False,staged=False),ensure_ascii=False))

if __name__=='__main__':main()
