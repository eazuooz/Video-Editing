"""Finite07.04 scalar-only audio preparation; default is read-only readiness.

Only --execute can invoke owned CPU FFmpeg/write a new immutable audio version.
Requires current blind raw-ASR, numerical word/join review and explicit internal
acceptance of the exact selected component identity. Never claims hearing.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,os,shutil,subprocess,uuid
from pathlib import Path
import numpy as np
import soundfile as sf
import scipy
from initialize import ROOT,HERE,MEDIA,AUTH_KEY,read,save

BASE_SHA='29b44bce108c38064a33be5c64f7956d673bb60017afe458c990ce7672390a1f'
CAPTION_SHA='705f6c3fa3c220b68ea524d24387c9ff399dbbfa9a6dab12a250766051c475fd'
QA_SHA='65983206f0e0fa81dd5a5780871605fcc2665816a9f21fc3ea3a43781437e2a9'
PROTOCOL='architectural111-07-04-audio-v1';OWNER='architectural-111-07-04-audio'
PROJECT=ROOT/'projects/shorts-leveldesign-07-04';TOPIC=MEDIA/PROJECT.name
VOICE=MEDIA/'07-04-voice-evidence.json';DEST=TOPIC/'audio-preparation-v1';WORKER=MEDIA/'07-04-audio-worker.json'
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)|getattr(subprocess,'BELOW_NORMAL_PRIORITY_CLASS',0)

def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
if sha(HERE/'prepare-first-audio.py')!=BASE_SHA:raise RuntimeError('Reviewed first-audio primitives changed; inspect before selected audio prep')
base=module('zen_audio_verified_first_primitives',HERE/'prepare-first-audio.py')
PROFILE=dict(base.PROFILE)
runtime=module('zen_audio_private_singleton',HERE/'run-first-native.py');runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER

class Pending(RuntimeError):pass

def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def pinned(row):
 p=Path(row['path']).resolve()
 if not p.is_file()or sha(p)!=row.get('sha256'):raise Pending('Pinned selected evidence changed: '+str(p))
 return pin(p)

def exact_components(evidence,timing):
 rate=evidence['aggregateWav']['sampleRate'];rows=[];position=0;scenes=evidence['identity']['scenes'];count=len(scenes)
 if rate!=24000 or not count or len({s['id']for s in scenes})!=count or len(evidence['sceneWavs'])!=count or len(timing['entries'])!=count or len(evidence['paragraphMapping'])!=count:raise Pending('Exact selected scene-identity count and canonical clock required')
 for take,entry,mapping,scene in zip(evidence['sceneWavs'],timing['entries'],evidence['paragraphMapping'],scenes):
  if entry['scene_id']!=mapping['sceneId']or entry['scene_id']!=scene['id']or entry['text']!=mapping['canonicalText']or entry['text']!=' '.join(scene['lines'])or take['sampleRate']!=rate or take['channels']!=1 or take['sampleWidthBytes']!=2:raise Pending('Component ordered identity/text/PCM format differs')
  end=position+take['frames']
  if abs(entry['start']-position/rate)>1e-9 or abs(entry['end']-end/rate)>1e-9:raise Pending('Component boundary differs from unrounded canonical samples')
  rows.append(dict(sceneId=mapping['sceneId'],paragraph=mapping['paragraph'],text=entry['text'],rawTake=take['path'],rawTakeSHA256=take['sha256'],rawPcmSHA256=take['pcmSHA256'],sourceSampleRange=[0,take['frames']],destinationSampleRange=[position,end],prepared48kSampleRange=[position*2,end*2],frames=take['frames'],rate=rate,startSeconds=position/rate,endSeconds=end/rate));position=end
 paragraphs=[r['paragraph']for r in rows]
 if position!=evidence['aggregateWav']['frames']or paragraphs!=sorted(paragraphs)or list(dict.fromkeys(paragraphs))!=list(range(1,8)):raise Pending('Selected components do not cover exactly seven ordered authored paragraphs')
 return rows

def historical_engine_pins(evidence):
 old=evidence.get('engineOutputsPreserved',{});pins=[]
 for k in ('aggregateWav','timing','srt'):
  if k in old:pins.append(pinned(old[k]))
 for row in old.get('existingArtifacts',[]):
  if 'preservedPath'in row:pins.append(pinned(dict(path=row['preservedPath'],sha256=row['sha256'])))
 if not pins:raise Pending('Historical engine aggregate/attempt evidence must remain preserved')
 return pins

def exact_level_review(path,voice,asr_pin,qa):
 path=Path(path).resolve();report=read(path);job=qa.prepare_job()
 primitive=HERE/'first-level-continuity-review.py'
 if sha(primitive)!=qa.APPROVED['firstLevelPrimitiveSHA256']:raise Pending('Reviewed numerical primitive changed')
 mathqa=module('zen_audio_existing_word_levels',primitive)
 if report.get('voiceFingerprint')!=voice['fingerprint']or report.get('canonicalWav')!=voice['aggregateWav']or report.get('asrReview')!=asr_pin or report.get('levelPrimitive')!=pin(primitive)or report.get('policy')!=mathqa.POLICY:raise Pending('Numerical level review belongs to another PCM/ASR/policy')
 fp=qa.digest(dict(asr=asr_pin,canonicalSHA256=voice['aggregateWav']['sha256'],primitive=pin(primitive),policy=mathqa.POLICY))
 expected=Path(job['output'])/'raw-level-review'/fp[:24]/'review.json'
 if path!=expected.resolve()or not expected.is_file():raise Pending('Current complete raw word/join level artifact required')
 # Existing file required above. Recompute through pinned trusted CPU primitive;
 # immutable_json can only verify the already-existing identical artifact here.
 if qa.raw_level_review(Path(job['output'])/'job.json').resolve()!=path:raise Pending('Numerical level proof recomputed to a different version')
 count=len(voice['identity']['scenes'])
 if len(report.get('takes',[]))!=count or len(report.get('paragraphs',[]))!=7 or len(report.get('joins',[]))!=count-1:raise Pending('Numerical review does not cover exact selected take/join identity')
 return report

def require_stable_takes(flags):
 if any(f.get('kind')=='sustained-take-word-body-decline'for f in flags):raise Pending('Within-take word-body decline requires source repair; uniform gain cannot correct it')

def proposal(voice,rows,review,levels,source_pins):
 require_stable_takes(levels['flags'])
 aggregate,rate=sf.read(voice['aggregateWav']['path'],dtype='float32');parts=[];component_rows=[]
 if rate!=24000 or aggregate.ndim!=1:raise Pending('Canonical mono24k voice required')
 for row in rows:
  if sha(row['rawTake'])!=row['rawTakeSHA256']:raise Pending('Raw component changed before scalar proposal')
  samples,sr=sf.read(row['rawTake'],dtype='float32');a,b=row['destinationSampleRange']
  if sr!=rate or not np.array_equal(samples,aggregate[a:b]):raise Pending('Canonical aggregate must exactly contain unchanged raw components; no fade exception here')
  matched,normalization=base.match_paragraph(samples,rate,PROFILE)
  recognized=next((r for r in review['takes']if r['task']['sceneId']==row['sceneId']),None)
  if recognized is None:raise Pending('Actual component blind-ASR record missing')
  component_rows.append(dict(**row,normalization=normalization,rawTakeASRRecordSHA256=digest(recognized),recognizedLiteral=recognized['text'],literalComparison=recognized['comparison'],literalDifferent=base.asr.folded(row['text'])!=base.asr.folded(recognized['text'])));parts.append(matched)
 normalized=np.concatenate(parts)
 if len(normalized)!=len(aggregate):raise Pending('Scalar copies changed canonical sample count')
 joins=[]
 for left,right in zip(component_rows,component_rows[1:]):
  k=left['destinationSampleRange'][1]
  joins.append(dict(previousScene=left['sceneId'],nextScene=right['sceneId'],boundarySample=k,rawLastSample=float(aggregate[k-1]),rawFirstSample=float(aggregate[k]),normalizedLastSample=float(normalized[k-1]),normalizedFirstSample=float(normalized[k]),normalizedAbsoluteStep=float(abs(normalized[k]-normalized[k-1])),insertedSamples=0,trimmedSamples=0,interpretation='Numerical boundary only; no click/hearing acceptance inferred.'))
 identity=dict(protocol=PROTOCOL,voiceFingerprint=voice['fingerprint'],selectedComponentCount=len(voice['identity']['scenes']),canonicalWavSHA256=voice['aggregateWav']['sha256'],canonicalPcmSHA256=voice['aggregateWav']['pcmSHA256'],timingSHA256=voice['timing']['sha256'],components=component_rows,joins=joins,levelFlags=levels['flags'],profile=PROFILE,sourcePins=source_pins,processorSHA256=sha(__file__),baseProcessorSHA256=BASE_SHA,numpyVersion=np.__version__,soundfileVersion=sf.__version__,libsndfileVersion=sf.__libsndfile_version__,scipyVersion=scipy.__version__)
 return dict(schemaVersion='07-04-scalar-audio-proposal-v1',identity=identity,fingerprint=digest(identity),joinsReviewedSHA256=digest(joins),acknowledgedLevelFlagsSHA256=digest(levels['flags']),automaticSpeechPass=False,actualListening=False,audioWritten=False)

def accepted_review(proposed,path,asr_pin,level_pin):
 r=read(path);identity=proposed['identity'];components=identity['components']
 require_stable_takes(identity['levelFlags']);count=identity['selectedComponentCount']
 required=dict(schemaVersion='07-04-accepted-audio-components-v1',topicId='07.04',componentCount=count,voiceFingerprint=identity['voiceFingerprint'],canonicalWavSHA256=identity['canonicalWavSHA256'],canonicalPcmSHA256=identity['canonicalPcmSHA256'],timingSHA256=identity['timingSHA256'],rawAsrReview=asr_pin,levelReview=level_pin,proposalFingerprint=proposed['fingerprint'],joinsReviewedSHA256=proposed['joinsReviewedSHA256'],acknowledgedLevelFlagsSHA256=proposed['acknowledgedLevelFlagsSHA256'],technicalOnly=True,actualListening=False,humanApproval=False)
 if any(r.get(k)!=v for k,v in required.items()):raise Pending('Accepted component review does not bind exact current proposal/ASR/level proofs')
 if not isinstance(r.get('reviewer'),str)or not r['reviewer'].strip():raise Pending('Factual internal reviewer identity required')
 if identity['levelFlags']and not str(r.get('levelFlagsDisposition','')).strip():raise Pending('Numerical warning dispositions are required; never silently pass them')
 decisions=r.get('components',[])
 if len(components)!=count or len(decisions)!=count or[d.get('sceneId')for d in decisions]!=[d['sceneId']for d in components]:raise Pending('Exact current component decisions must all be present in identity order')
 for decision,source in zip(decisions,components):
  for k in ('sceneId','rawTakeSHA256','rawPcmSHA256','rawTakeASRRecordSHA256'):
   if decision.get(k)!=source[k]:raise Pending('Accepted component identity changed')
  if decision.get('decision')!='accept-scalar-match'or decision.get('literalDecision')!='accepted':raise Pending('Component remains declined/held; no normalization fallback permitted')
  gain=decision.get('expectedGainDb')
  if type(gain)not in(int,float)or not math.isfinite(gain)or abs(gain-source['normalization']['constantGainDb'])>1e-7:raise Pending('Accepted safe scalar gain differs')
  if source['literalDifferent']and not str(decision.get('literalReviewNote','')).strip():raise Pending('Literal difference needs an explicit retained review note')
  if abs(source['normalization']['targetErrorDb'])>.5 and not str(decision.get('levelReviewNote','')).strip():raise Pending('Peak-limited target needs an explicit numerical acceptance note')
 return r

def prepare(asr_path=None,level_path=None,component_path=None):
 auth=read(ROOT/'shared/publishing/video-production-control.json')[AUTH_KEY]
 if auth['status']in('paused','stopped','cancelled')or not auth['automaticAdvanceWithinExactList']or auth['automaticAdvanceOutsideList']:raise Pending('Selected111 authorization inactive')
 if not asr_path or not level_path:raise Pending('Current completed raw-ASR and numerical word/join level-review paths required')
 if sha(HERE/'build-selected-caption-timing.py')!=CAPTION_SHA or sha(HERE/'run-selected-voice-qa.py')!=QA_SHA:raise Pending('Reviewed selected voice/ASR binding source changed')
 caption=module('zen_audio_current_caption_binding',HERE/'build-selected-caption-timing.py');qa=module('zen_audio_current_raw_qa',HERE/'run-selected-voice-qa.py')
 voice=read(VOICE);asr_pin=pin(asr_path);review=caption.verified_asr_review(asr_path);binding=caption.voice_binding(voice,review,read(PROJECT/'narration-draft.json'))
 levels=exact_level_review(level_path,voice,asr_pin,qa);level_pin=pin(level_path);rows=exact_components(voice,read(voice['timing']['path']))
 if sha(base.MUSIC)!=base.MUSIC_SHA or not base.LICENSE.is_file():raise Pending('Approved BGM/CCBY credit source missing or changed')
 credit=base.LICENSE.read_text(encoding='utf-8')
 if 'Creative Commons Attribution 4.0'not in credit or 'Kevin MacLeod'not in credit:raise Pending('Approved music attribution missing')
 if not base.FF.is_file()or not base.FF.with_name('ffprobe.exe').is_file():raise Pending('Reviewed installed FFmpeg/FFprobe tools required')
 source_pins=[pin(p)for p in [VOICE,PROJECT/'narration-draft.json',HERE/'build-selected-caption-timing.py',HERE/'run-selected-voice-qa.py',HERE/'prepare-first-audio.py',HERE/'first-level-continuity-review.py',base.MUSIC,base.LICENSE,Path(asr_path),Path(level_path),base.FF,base.FF.with_name('ffprobe.exe')]]+[pinned(voice['timing']),pinned(voice['aggregateWav'])]+historical_engine_pins(voice)
 proposed=proposal(voice,rows,review,levels,source_pins)
 context=dict(voice=voice,rows=rows,proposal=proposed,binding=binding,asrPin=asr_pin,levelPin=level_pin)
 if not component_path:return context,None
 decision=accepted_review(proposed,component_path,asr_pin,level_pin)
 identity=dict(proposalFingerprint=proposed['fingerprint'],acceptedReview=pin(component_path),musicSHA256=base.MUSIC_SHA,profile=PROFILE,processorSHA256=sha(__file__),ffmpegPath=str(base.FF))
 return context,dict(identity=identity,fingerprint=digest(identity),acceptedReview=decision)

def artifact(folder,name):
 p=folder/name;info=sf.info(p)
 return dict(path=str(p),sha256=sha(p),sampleRate=info.samplerate,channels=info.channels,frames=info.frames,durationSeconds=info.frames/info.samplerate,subtype=info.subtype)

def tracked_run(worker,command):
 command=[str(a)for a in command]
 if Path(command[0]).resolve()not in(base.FF.resolve(),base.FF.with_name('ffprobe.exe').resolve()):raise Pending('Only owned approved CPU audio tools may launch')
 if Path(command[0]).name.lower()=='ffmpeg.exe':command=command[:1]+['-threads','2','-filter_threads','2']+command[1:]
 worker.update(phase='launching-owned-cpu-audio-tool',launchCommand=command,child=None)
 child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=CREATE);worker.update(child=runtime.identity(child.pid),phase='owned-cpu-audio-tool')
 out,err=child.communicate();worker.update(child=None,phase='audio-cpu-processing')
 if child.returncode:raise RuntimeError(err.decode(errors='replace')[-5000:])
 return subprocess.CompletedProcess(command,child.returncode,out,err)

def unrecorded_audio_child(record):
 if not record or record.get('phase')!='launching-owned-cpu-audio-tool':return False
 command=record.get('launchCommand')
 if not command:return True
 for p in runtime.psutil.process_iter(['name','cmdline']):
  try:
   if(p.info.get('name')or'').lower()!=Path(command[0]).name.lower():continue
   if p.info['cmdline']is None:return True
   if p.info['cmdline']==command:return True
  except runtime.psutil.NoSuchProcess:continue
  except runtime.psutil.AccessDenied:return True
 return False

def owned_audio_alive(record):return runtime.alive(record)or unrecorded_audio_child(record)

def reuse_audio(folder,recipe):
 old=read(folder/'audio-build.json')
 if old.get('schemaVersion')!='07-04-audio-build-v1'or old.get('topicId')!='07.04'or old.get('fingerprint')!=recipe['fingerprint']:raise Pending('Preserve differing old audio version')
 for row in old['artifacts'].values():
  source=(folder/row['file']).resolve()
  if not source.is_relative_to(folder.resolve())or sha(source)!=row['sha256']:raise Pending('Previously prepared audio changed or escaped owned folder')
 if old.get('mixWav')!=artifact(folder,'final-mix.wav'):raise Pending('Existing hash-bound mix descriptor differs from actual file')
 return old

def execute(asr_path,level_path,component_path):
 worker=runtime.SingleWorker(WORKER,is_alive=owned_audio_alive).acquire();worker.update(stage='CPU-audio',topicId='07.04')
 original_run=base.run;work=None
 try:
  ctx,recipe=prepare(asr_path,level_path,component_path)
  if recipe is None:raise Pending('Explicit acceptance of every exact selected component required before mix')
  folder=DEST/recipe['fingerprint'][:24]
  if folder.exists():
   return reuse_audio(folder,recipe)
  if shutil.disk_usage(TOPIC).free<2*1024**3:raise Pending('Insufficient C reserve; preserve original audio/media')
  work=DEST/('work-'+recipe['fingerprint'][:16]+'-'+uuid.uuid4().hex[:8]);work.mkdir(parents=True,exist_ok=False)
  save(work/'input-recipe.json',dict(**recipe,proposal=ctx['proposal'],voiceBinding=ctx['binding']))
  parts=[];records=[];rate=24000
  for source in ctx['proposal']['identity']['components']:
   samples,sr=sf.read(source['rawTake'],dtype='float32');matched,measure=base.match_paragraph(samples,sr,PROFILE)
   if sr!=rate or measure!=source['normalization']:raise Pending('Approved scalar proposal changed before normalization')
   name=source['sceneId']+'-normalized.wav';sf.write(work/name,matched,rate,subtype='FLOAT');parts.append(matched);records.append(dict(**source,normalizedTake=name,normalizedTakeSHA256=sha(work/name)))
  normalized=np.concatenate(parts);voice=ctx['voice'];frames=voice['aggregateWav']['frames']
  if len(normalized)!=frames:raise Pending('Normalized voice length differs from canonical raw samples')
  norm=work/'narration-component-normalized.wav';sf.write(norm,normalized,rate,subtype='FLOAT')
  linelevels=dict(schemaVersion='07-04-line-levels-v1',componentCount=len(voice['identity']['scenes']),policy=PROFILE['policy'],voiceFingerprint=voice['fingerprint'],rawCanonical=voice['aggregateWav'],components=records,paragraphs=[dict(paragraph=n,sceneIds=[r['sceneId']for r in records if r['paragraph']==n],destinationSampleRange=[min(r['destinationSampleRange'][0]for r in records if r['paragraph']==n),max(r['destinationSampleRange'][1]for r in records if r['paragraph']==n)])for n in range(1,8)],joins=ctx['proposal']['identity']['joins'],rawRate=rate,frames=frames,durationSeconds=frames/rate,normalizedCopyOnly=True,originalRawFilesUnchanged=True,amplitudeOnlyScalarCopies=True,wordBoundariesShifted=False,voiceOffsetSeconds=0.,insertedSamples=0,trimmedSamples=0,voiceSpeed=1.,compressorUsed=False,voiceSideDuck=False,actualListening=False,automaticSpeechPass=False)
  save(work/'line-levels.json',linelevels)
  prepared=base.stereo_voice(normalized,rate);pp=work/'narration-prepared-stem.wav';sf.write(pp,prepared,48000,subtype='FLOAT')
  base.run=lambda command:tracked_run(worker,command)
  voice_gain,voice_levels=base.fixed_gain(prepared,base.loud(pp),PROFILE['voiceTargetLufs'],PROFILE['voiceSamplePeakCeilingDbfs']);stem=prepared*voice_gain
  native_info=json.loads(base.run([base.FF.with_name('ffprobe.exe'),'-v','error','-select_streams','a:0','-show_entries','stream=sample_rate,channels,duration','-of','json',base.MUSIC]).stdout)['streams'][0]
  data=base.run([base.FF,'-v','error','-i',base.MUSIC,'-map','0:a:0','-ar','48000','-ac','2','-f','f32le','pipe:1']).stdout
  music=np.frombuffer(data,dtype='<f4').reshape(-1,2).copy()
  if not np.isfinite(music).all():raise Pending('Nonfinite music decode')
  music_gain,music_levels=base.fixed_gain(music,base.loud(base.MUSIC),PROFILE['musicTargetLufs'],PROFILE['musicSamplePeakCeilingDbfs'])
  bed=base.music_bed(music,len(stem),48000,music_gain,base.duck_curve(stem,48000,PROFILE),PROFILE)
  combined=stem+bed;overall=min(1.,10**((PROFILE['mixSamplePeakCeilingDbfs']-base.db(np.max(np.abs(combined))))/20))
  measured=None
  for attempt in range(2):
   trial=work/f'mix-measurement-{attempt+1}.wav';sf.write(trial,combined*overall,48000,subtype='FLOAT');measured=base.loud(trial)
   if float(measured['input_tp'])<=PROFILE['mixTruePeakMaximumDbtp']:break
   overall*=10**((PROFILE['mixTruePeakMaximumDbtp']-float(measured['input_tp'])-.35)/20)
  else:raise Pending('Actual true-peak blocker; preserve work, no compressor/limiter fallback')
  for name,values in [('narration-stem.wav',stem*overall),('music-stem.wav',bed*overall),('final-mix.wav',combined*overall)]:
   if not np.isfinite(values).all():raise Pending('Nonfinite processed audio')
   sf.write(work/name,values,48000,subtype='FLOAT')
  if prepare(asr_path,level_path,component_path)[1]['fingerprint']!=recipe['fingerprint']:raise Pending('Selected inputs changed during preparation; preserve work')
  names=[p.name for p in work.iterdir()if p.is_file()];artifacts={name:dict(file=name,sha256=sha(work/name))for name in names}
  mix=artifact(work,'final-mix.wav');mix['path']=str(folder/'final-mix.wav')
  result=dict(schemaVersion='07-04-audio-build-v1',topicId='07.04',status='audio-prepared-mixed-ASR-and-listening-pending',fingerprint=recipe['fingerprint'],output=str(folder),artifacts=artifacts,mixWav=mix,selectedComponentCount=len(voice['identity']['scenes']),rawVoice=voice['aggregateWav'],rawVoiceFingerprint=voice['fingerprint'],canonicalTiming=voice['timing'],normalizedVoiceFrames=frames,normalizedVoiceRate=rate,mixFrames=len(stem),mixRate=48000,durationSeconds=frames/rate,videoFrameTarget=dict(fps=60,totalFrames=math.ceil(frames*60/rate),noAudioTailPadding=True),voiceGlobalGain=voice_levels,musicGain=music_levels,musicNativeStream=native_info,musicAttribution=base.LICENSE.read_text(encoding='utf-8').split('Credit for the description:\n\n')[-1].strip(),musicContinuousExcerpt=True,musicLoops=0,musicPlaybackRate=1.,musicSourceStartSeconds=0.,musicFadeSeconds=.45,musicSpeechDuckDb=4.,compressorUsed=False,voiceSideDuck=False,uniformMixGainDb=base.db(overall),measuredPcmMix=measured,originalRawFilesUnchanged=True,wordBoundariesShifted=False,voiceOffsetSeconds=0.,insertedSamples=0,trimmedSamples=0,historicalEngineAggregatePreserved=True,acceptedComponentsReview=pin(component_path),rawVoiceAsr=ctx['asrPin'],rawNumericalLevelReview=ctx['levelPin'],actualListening=False,automaticSpeechPass=False,finalMixedAsr='pending-exact-selected-mix-windows',encodedAacTruePeak='pending',encodedAlignedLevelReview='pending',finalMovieComplete=False,humanApproval=False)
  save(work/'audio-build.json',result)
  if folder.exists():raise Pending('Final version appeared; preserve both outputs')
  work.rename(folder);return result
 except BaseException as error:
  if work and work.exists()and not(work/'failed.json').exists():save(work/'failed.json',dict(complete=False,error=str(error),automaticFallback=False,actualListening=False))
  raise
 finally:
  base.run=original_run;worker.close(remove=not runtime.alive(worker.record.get('child'))and not unrecorded_audio_child(worker.record))

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--asr-review');p.add_argument('--level-review');p.add_argument('--component-review');p.add_argument('--proposal-only',action='store_true');p.add_argument('--execute',action='store_true');a=p.parse_args()
 try:
  if a.execute:
   if a.proposal_only:raise Pending('Proposal cannot execute a mix')
   result=execute(a.asr_review,a.level_review,a.component_review);print(json.dumps(result,ensure_ascii=False))
  else:
   ctx,recipe=prepare(a.asr_review,a.level_review,a.component_review)
   print(json.dumps(ctx['proposal']if a.proposal_only else dict(ready=recipe is not None,requires=None if recipe else'Explicit acceptance of exact selected component identity',componentCount=len(ctx['voice']['identity']['scenes']),fingerprint=recipe['fingerprint']if recipe else None,rawVoiceFrames=ctx['voice']['aggregateWav']['frames'],audioPrepared=False,ffmpegStarted=False,gpuUsed=False),ensure_ascii=False))
 except Pending as e:
  print(json.dumps(dict(ready=False,reason=str(e),audioPrepared=False,automaticFallback=False,hearingClaimed=False),ensure_ascii=False));return 2 if a.execute else 0
 return 0

if __name__=='__main__':raise SystemExit(main())
