"""Finite06.02 103-component scalar-only audio preparation V2; default is read-only readiness.

Only --execute can invoke owned CPU FFmpeg/write a new immutable audio version.
Requires current blind raw-ASR, numerical word/join review and explicit internal
acceptance of the exact selected component identity. Never claims hearing.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,os,re,shutil,subprocess,uuid
from pathlib import Path
import numpy as np
import soundfile as sf
import scipy
from initialize import ROOT,HERE,MEDIA,AUTH_KEY,read,save

PREVIOUS_AUDIO_SHA='363b7e22bd99e1b860d981b12c2d91a965f740b3b77ec00935c74db456f6ed7b'
BASE_SHA='29b44bce108c38064a33be5c64f7956d673bb60017afe458c990ce7672390a1f'
CAPTION_FILE='build-prospect-refuge-caption-timing-v2.py'
CAPTION_SHA='1b15170b292d6acc557e4bd1b0dbbbf6aaf4a7cd4d64a8a51c800b693df6fee8'
QA_FILE='run-prospect-refuge-voice-qa-v2.py'
QA_SHA='f190897764f2088fe8de425c622444a75ec6f5a4185763af5a02faa4a0caf4b1'
PROTOCOL='architectural111-06-02-audio-v2';OWNER='architectural-111-06-02-audio'
PROJECT=ROOT/'projects/shorts-leveldesign-06-02';TOPIC=MEDIA/PROJECT.name
VOICE=MEDIA/'06-02-voice-evidence.json';DEST=TOPIC/'audio-preparation-v2';WORKER=MEDIA/'06-02-audio-worker.json'
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)|getattr(subprocess,'BELOW_NORMAL_PRIORITY_CLASS',0)

def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
if sha(HERE/'prepare-zen-view-audio.py')!=PREVIOUS_AUDIO_SHA:raise RuntimeError('Reviewed previous audio source changed')
if sha(HERE/'prepare-first-audio.py')!=BASE_SHA:raise RuntimeError('Reviewed first-audio primitives changed; inspect before selected audio prep')
base=module('zen_audio_verified_first_primitives',HERE/'prepare-first-audio.py')
PROFILE=dict(base.PROFILE)
MUSIC=ROOT/'shared/assets/music/incompetech/Wholesome.mp3'
MUSIC_SHA='9eadc79a1a2cb68cd63be1432ebf8f8ae3387cb9d2e85f9b8dbc74ba5a96b231'
LICENSE=MUSIC.with_suffix('.LICENSE.md')
LICENSE_SHA='3331347694f00cabcd30f4d72a974ec451f5aae153d944dfc28741682937a535'
MUSIC_LOOP_POLICY=dict(id='approved-bgm-one-second-crossfade-v1',crossfadeSeconds=1.,curve='linear-complementary',sourcePlaybackRate=1.,speechTrimOrWarpAllowed=False,sourceStartSamplePerRepeat=0,outerFadeSeconds=.45,rule='docs/NARRATION_AUDIO_STANDARD.md: 곡 반복 1초 크로스페이드')
base.MUSIC=MUSIC;base.MUSIC_SHA=MUSIC_SHA;base.LICENSE=LICENSE
MUSIC_BALANCE_POLICY=dict(id='music-only-unreached-voice-target-v1',
 formula='min(0, voice.constantGainDb - voice.desiredGainDb)',
 application='One extra scalar after the existing nominal music excerpt/duck/fades',
 musicBoostAllowed=False,voiceGainOrPcmChangeAllowed=False,uniformMixGainDb=0.,
 peakFailureAction='Hold for review; never attenuate the unchanged voice as a fallback')
runtime=module('zen_audio_private_singleton',HERE/'run-first-native.py');runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER

class Pending(RuntimeError):pass

def music_headroom_compensation(voice_levels):
 """Pure finite scalar: restore nominal relative headroom, never boost music."""
 values=[]
 for key in ('constantGainDb','desiredGainDb'):
  value=voice_levels.get(key)
  if type(value)not in(int,float)or not math.isfinite(value):raise Pending('Finite actual/desired voice gain required for music-only compensation')
  values.append(value)
 actual,desired=values;difference=actual-desired
 if not math.isfinite(difference):raise Pending('Nonfinite voice target shortfall')
 delta=min(0.,difference);factor=10**(delta/20)
 if not math.isfinite(factor)or not 0<factor<=1:raise Pending('Music-only factor must be finite, positive and never boost')
 return dict(policy=dict(MUSIC_BALANCE_POLICY),voiceConstantGainDb=actual,voiceDesiredGainDb=desired,
  compensationDb=delta,linearFactor=factor,voicePcmOrGainChanged=False,musicBoosted=False,
  reason='When the unchanged voice cannot reach its nominal target, lower only the music by the same shortfall; no hearing/SNR pass is inferred')

def apply_music_compensation(nominal_bed,compensation):
 """Keep the original music phase/duck/fades and every sample position."""
 if not isinstance(nominal_bed,np.ndarray)or nominal_bed.dtype!=np.float32 or nominal_bed.ndim!=2 or nominal_bed.shape[1]!=2 or not len(nominal_bed)or not np.isfinite(nominal_bed).all():raise Pending('Finite nonempty FLOAT32 stereo nominal music bed required')
 expected=music_headroom_compensation(dict(constantGainDb=compensation['voiceConstantGainDb'],desiredGainDb=compensation['voiceDesiredGainDb']))
 if compensation!=expected:raise Pending('Music-only compensation proof differs from exact finite formula')
 bed=nominal_bed*compensation['linearFactor']
 return bed,dict(**compensation,frames=len(bed),channels=2,sampleRate=48000,
  nominalBedFloat32PcmSHA256=hashlib.sha256(nominal_bed.astype('<f4',copy=False).tobytes()).hexdigest(),
  effectiveBedFloat32PcmSHA256=hashlib.sha256(bed.astype('<f4',copy=False).tobytes()).hexdigest(),
  scalarAppliedAfterDuckAndFades=True,phaseOrEnvelopeTimingChanged=False,insertedSamples=0,trimmedSamples=0)

def effective_music_levels(nominal,compensation):
 result=dict(nominal)
 for key in ('targetLufs','constantGainDb','desiredGainDb'):
  value=nominal.get(key)
  if type(value)not in(int,float)or not math.isfinite(value):raise Pending('Finite nominal music gain/target metadata required')
  result[key]=value+compensation['compensationDb']
 result.update(nominalTargetLufs=nominal['targetLufs'],nominalConstantGainDb=nominal['constantGainDb'],
  nominalDesiredGainDb=nominal['desiredGainDb'],musicOnlyCompensationDb=compensation['compensationDb'],
  effectiveGainIncludesMusicOnlyCompensation=True)
 return result

def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def pinned(row):
 p=Path(row['path']).resolve()
 if not p.is_file()or sha(p)!=row.get('sha256'):raise Pending('Pinned selected evidence changed: '+str(p))
 return pin(p)

def exact_components(evidence,timing):
 rate=evidence['aggregateWav']['sampleRate'];rows=[];position=0;scenes=evidence['identity']['scenes'];count=len(scenes)
 if rate!=24000 or count!=103 or len({s['id']for s in scenes})!=count or len(evidence['sceneWavs'])!=count or len(timing['entries'])!=count or len(evidence['paragraphMapping'])!=count:raise Pending('Exact selected103 physical scene-identity count and canonical clock required')
 for take,entry,mapping,scene in zip(evidence['sceneWavs'],timing['entries'],evidence['paragraphMapping'],scenes):
  if not re.fullmatch(r'[A-Za-z0-9_-]+',scene['id'])or type(take['frames'])is not int or take['frames']<=0:raise Pending('Canonical nonempty component id/frame contract required')
  if entry['scene_id']!=mapping['sceneId']or entry['scene_id']!=scene['id']or entry['text']!=mapping['canonicalText']or entry['text']!=' '.join(scene['lines'])or take['sampleRate']!=rate or take['channels']!=1 or take['sampleWidthBytes']!=2:raise Pending('Component ordered identity/text/PCM format differs')
  end=position+take['frames']
  if abs(entry['start']-position/rate)>1e-9 or abs(entry['end']-end/rate)>1e-9:raise Pending('Component boundary differs from unrounded canonical samples')
  rows.append(dict(sceneId=mapping['sceneId'],paragraph=mapping['paragraph'],text=entry['text'],rawTake=take['path'],rawTakeSHA256=take['sha256'],rawPcmSHA256=take['pcmSHA256'],sourceSampleRange=[0,take['frames']],destinationSampleRange=[position,end],prepared48kSampleRange=[position*2,end*2],frames=take['frames'],rate=rate,startSeconds=position/rate,endSeconds=end/rate));position=end
 paragraphs=[r['paragraph']for r in rows]
 if position!=evidence['aggregateWav']['frames']or paragraphs!=sorted(paragraphs)or list(dict.fromkeys(paragraphs))!=list(range(1,26)):raise Pending('Selected components do not cover exactly twenty-five ordered authored paragraphs')
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
 if sha(primitive)!=qa.qa.APPROVED['firstLevelPrimitiveSHA256']:raise Pending('Reviewed numerical primitive changed')
 mathqa=module('zen_audio_existing_word_levels',primitive)
 if report.get('voiceFingerprint')!=voice['fingerprint']or report.get('canonicalWav')!=voice['aggregateWav']or report.get('asrReview')!=asr_pin or report.get('levelPrimitive')!=pin(primitive)or report.get('policy')!=mathqa.POLICY:raise Pending('Numerical level review belongs to another PCM/ASR/policy')
 fp=qa.digest(dict(asr=asr_pin,canonicalSHA256=voice['aggregateWav']['sha256'],primitive=pin(primitive),policy=mathqa.POLICY))
 expected=Path(job['output'])/'raw-level-review'/fp[:24]/'review.json'
 if path!=expected.resolve()or not expected.is_file():raise Pending('Current complete raw word/join level artifact required')
 # Existing file required above. Recompute through pinned trusted CPU primitive;
 # immutable_json can only verify the already-existing identical artifact here.
 if qa.raw_level_review(Path(job['output'])/'job.json').resolve()!=path:raise Pending('Numerical level proof recomputed to a different version')
 count=len(voice['identity']['scenes'])
 if len(report.get('takes',[]))!=count or len(report.get('paragraphs',[]))!=25 or len(report.get('joins',[]))!=count-1:raise Pending('Numerical review does not cover exact selected take/join identity')
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
 identity=dict(protocol=PROTOCOL,voiceFingerprint=voice['fingerprint'],selectedComponentCount=len(voice['identity']['scenes']),canonicalWavSHA256=voice['aggregateWav']['sha256'],canonicalPcmSHA256=voice['aggregateWav']['pcmSHA256'],timingSHA256=voice['timing']['sha256'],components=component_rows,joins=joins,levelFlags=levels['flags'],profile=PROFILE,musicBalancePolicy=MUSIC_BALANCE_POLICY,musicLoopPolicy=MUSIC_LOOP_POLICY,sourcePins=source_pins,processorSHA256=sha(__file__),baseProcessorSHA256=BASE_SHA,previousAudioProcessorSHA256=PREVIOUS_AUDIO_SHA,numpyVersion=np.__version__,soundfileVersion=sf.__version__,libsndfileVersion=sf.__libsndfile_version__,scipyVersion=scipy.__version__)
 return dict(schemaVersion='06-02-scalar-audio-proposal-v1',identity=identity,fingerprint=digest(identity),joinsReviewedSHA256=digest(joins),acknowledgedLevelFlagsSHA256=digest(levels['flags']),automaticSpeechPass=False,actualListening=False,audioWritten=False)

def accepted_review(proposed,path,asr_pin,level_pin):
 r=read(path);identity=proposed['identity'];components=identity['components']
 require_stable_takes(identity['levelFlags']);count=identity['selectedComponentCount']
 required=dict(schemaVersion='06-02-accepted-audio-components-v1',topicId='06.02',componentCount=count,voiceFingerprint=identity['voiceFingerprint'],canonicalWavSHA256=identity['canonicalWavSHA256'],canonicalPcmSHA256=identity['canonicalPcmSHA256'],timingSHA256=identity['timingSHA256'],rawAsrReview=asr_pin,levelReview=level_pin,proposalFingerprint=proposed['fingerprint'],joinsReviewedSHA256=proposed['joinsReviewedSHA256'],acknowledgedLevelFlagsSHA256=proposed['acknowledgedLevelFlagsSHA256'],technicalOnly=True,actualListening=False,humanApproval=False)
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
 if any(abs(j['rawLastSample']-j['rawFirstSample'])>.02 or j['normalizedAbsoluteStep']>.02 for j in identity['joins'])and not str(r.get('joinLevelReviewNote','')).strip():raise Pending('Large raw/normalized boundary sample jump needs an explicit retained technical review note; no silent acceptance')
 return r

def music_rights():
 if not MUSIC.is_file()or sha(MUSIC)!=MUSIC_SHA or not LICENSE.is_file()or sha(LICENSE)!=LICENSE_SHA:raise Pending('Approved calmer Wholesome source/license changed')
 text=LICENSE.read_text(encoding='utf8');marker='Credit for the description:\n\n'
 if marker not in text or 'Creative Commons Attribution 4.0'not in text or 'Kevin MacLeod'not in text:raise Pending('Required exact Wholesome attribution missing')
 credit=text.split(marker,1)[1].strip()
 return dict(title='Wholesome',composer='Kevin MacLeod',source=pin(MUSIC),licenseRecord=pin(LICENSE),sourceUrl='https://incompetech.com/music/royalty-free/mp3-royaltyfree/Wholesome.mp3',license='CC BY4.0',licenseUrl='https://creativecommons.org/licenses/by/4.0/',requiredDescriptionCredit=credit,modificationsToDisclose='Excerpting or repeated1x playback with music-only1-second crossfades, gain changes, speech ducking and outer fades as actually used.',previousUserChoice='Calmer Wholesome selected2026-09-26; existing rights/selection reused, not a fresh listening claim.',nominalContainerDurationSeconds=363.807350,actualDecodedDurationPending=True,discoveryExcludedBecause='Earlier ContentID claim recorded in the selected Wholesome license record',actualCurrentMusicListening=False,lyricsOrInstrumentalAuditionClaimed=False)

def loop_plan(source_frames,target_frames,rate):
 if any(type(v)is not int or v<=0 for v in(source_frames,target_frames,rate)):raise Pending('Positive integer music source/output sample clocks required')
 fade=round(MUSIC_LOOP_POLICY['crossfadeSeconds']*rate)
 if fade<2 or source_frames<=2*fade:raise Pending('Music source must have more than two crossfade windows; no degenerate repetition')
 stride=source_frames-fade;starts=[0]
 while starts[-1]+source_frames<target_frames:starts.append(starts[-1]+stride)
 segments=[];seams=[]
 for i,start in enumerate(starts):
  length=min(source_frames,target_frames-start);segments.append(dict(index=i,sourceSampleRange=[0,length],destinationSampleRange=[start,start+length],sourcePlaybackRate=1.,crossfadeInSamples=fade if i else 0,crossfadeOutSamples=fade if i<len(starts)-1 else 0))
  if i:seams.append(dict(previousSegment=i-1,nextSegment=i,destinationSampleRange=[start,start+fade],outgoingSourceSampleRange=[source_frames-fade,source_frames],incomingSourceSampleRange=[0,fade],curve='linear-complementary',speechAffected=False))
 return dict(policy=dict(MUSIC_LOOP_POLICY),sampleRate=rate,channels=2,sourceFrames=source_frames,targetFrames=target_frames,sourceDurationSeconds=source_frames/rate,outputDurationSeconds=target_frames/rate,sourceCopies=len(starts),repeatCount=len(starts)-1,crossfadeSamples=fade,segments=segments,seams=seams,continuousSingleExcerpt=len(starts)==1,speechSamplesChanged=False,speechInsertedSamples=0,speechTrimmedSamples=0)

def float_pcm_sha(values):
 value=np.asarray(values,dtype='<f4');digest_pcm=hashlib.sha256()
 for at in range(0,len(value),65536):digest_pcm.update(value[at:at+65536].tobytes())
 return digest_pcm.hexdigest()

def loop_music(source,count,rate):
 if not isinstance(source,np.ndarray)or source.dtype!=np.float32 or source.ndim!=2 or source.shape[1]!=2 or not np.isfinite(source).all():raise Pending('Finite FLOAT32 stereo decoded music required')
 plan=loop_plan(len(source),count,rate);out=np.zeros((count,2),dtype=np.float32);fade=plan['crossfadeSamples'];up=np.linspace(0,1,fade,dtype=np.float32)
 for segment in plan['segments']:
  begin,end=segment['destinationSampleRange'];size=end-begin;part=source[:size].copy()
  if segment['crossfadeInSamples']:part[:fade]*=up[:,None]
  if segment['crossfadeOutSamples']:part[-fade:]*=(1-up)[:,None]
  out[begin:end]+=part
 if not np.isfinite(out).all():raise Pending('Nonfinite music-only crossfade result')
 # Complementary linear weights prevent a seam from adding a second full music
 # layer. Do not normalize or gate the voice to hide a music join.
 if float(np.max(np.abs(out)))>float(np.max(np.abs(source)))+2e-7:raise Pending('Music-only overlap exceeded original peak envelope')
 plan.update(sourceFloat32PcmSHA256=float_pcm_sha(source),assembledFloat32PcmSHA256=float_pcm_sha(out),actualMusicOnlyCrossfadeApplied=bool(plan['seams']),sourceArrayFloat32Stereo=True,actualListening=False)
 for seam in plan['seams']:
  a,b=seam['destinationSampleRange'];seam['actualMusicBoundarySamples']=dict(before=out[a-1].tolist()if a else None,at=out[a].tolist(),lastOverlap=out[b-1].tolist(),after=out[b].tolist()if b<len(out)else None)
 return out,plan

def prepare(asr_path=None,level_path=None,component_path=None):
 auth=read(ROOT/'shared/publishing/video-production-control.json')[AUTH_KEY]
 if auth['status']in('paused','stopped','cancelled')or not auth['automaticAdvanceWithinExactList']or auth['automaticAdvanceOutsideList']:raise Pending('Selected111 authorization inactive')
 if not asr_path or not level_path:raise Pending('Current completed raw-ASR and numerical word/join level-review paths required')
 if CAPTION_SHA is None or QA_SHA is None or not(HERE/CAPTION_FILE).is_file()or not(HERE/QA_FILE).is_file():raise Pending('CPU-audited06 caption/ASR adapter freeze pending')
 if sha(HERE/CAPTION_FILE)!=CAPTION_SHA or sha(HERE/QA_FILE)!=QA_SHA:raise Pending('Reviewed selected voice/ASR binding source changed')
 caption=module('prospect_audio_current_caption_binding',HERE/CAPTION_FILE);qa=module('prospect_audio_current_raw_qa',HERE/QA_FILE)
 if not VOICE.is_file():raise Pending('Exact selected06 voice generation still pending')
 voice=read(VOICE);asr_pin=pin(asr_path);review=caption.verified_asr_review(asr_path);binding=caption.voice_binding(voice,review,read(PROJECT/'narration-expanded-draft-v4.json'))
 if len(voice['identity']['scenes'])!=103 or len(binding.get('sentences',[]))!=96:raise Pending('Selected103 physical components must bind exact96 logical viewer sentences')
 components=read(PROJECT/'voice-semantic-components-v3.json')
 if components.get('sourceNarrationSHA256')!=sha(PROJECT/'narration-expanded-draft-v4.json') or len(components.get('logicalGroups',[]))!=96:raise Pending('Current103-to96 semantic source is stale')
 levels=exact_level_review(level_path,voice,asr_pin,qa);level_pin=pin(level_path);rows=exact_components(voice,read(voice['timing']['path']))
 if sha(MUSIC)!=MUSIC_SHA or not LICENSE.is_file()or sha(LICENSE)!=LICENSE_SHA:raise Pending('Approved BGM/CCBY credit source missing or changed')
 credit=base.LICENSE.read_text(encoding='utf-8')
 if 'Creative Commons Attribution 4.0'not in credit or 'Kevin MacLeod'not in credit:raise Pending('Approved music attribution missing')
 if not base.FF.is_file()or not base.FF.with_name('ffprobe.exe').is_file():raise Pending('Reviewed installed FFmpeg/FFprobe tools required')
 source_pins=[pin(p)for p in [VOICE,PROJECT/'narration-expanded-draft-v4.json',PROJECT/'voice-semantic-components-v3.json',HERE/CAPTION_FILE,HERE/QA_FILE,HERE/'prepare-first-audio.py',HERE/'prepare-zen-view-audio.py',HERE/'first-level-continuity-review.py',ROOT/'docs/NARRATION_AUDIO_STANDARD.md',base.MUSIC,base.LICENSE,Path(asr_path),Path(level_path),base.FF,base.FF.with_name('ffprobe.exe')]]+[pinned(voice['timing']),pinned(voice['aggregateWav'])]+historical_engine_pins(voice)
 proposed=proposal(voice,rows,review,levels,source_pins)
 context=dict(voice=voice,rows=rows,proposal=proposed,binding=binding,asrPin=asr_pin,levelPin=level_pin)
 context['musicRights']=music_rights()
 if not component_path:return context,None
 decision=accepted_review(proposed,component_path,asr_pin,level_pin)
 identity=dict(proposalFingerprint=proposed['fingerprint'],acceptedReview=pin(component_path),musicSHA256=base.MUSIC_SHA,profile=PROFILE,musicBalancePolicy=MUSIC_BALANCE_POLICY,musicLoopPolicy=MUSIC_LOOP_POLICY,processorSHA256=sha(__file__),ffmpegPath=str(base.FF))
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
 if old.get('schemaVersion')!='06-02-audio-build-v1'or old.get('topicId')!='06.02'or old.get('fingerprint')!=recipe['fingerprint']:raise Pending('Preserve differing old audio version')
 required={'input-recipe.json','line-levels.json','narration-component-normalized.wav','narration-prepared-stem.wav','narration-stem.wav','music-stem.wav','final-mix.wav','music-loop-plan.json'}
 if not required<=set(old.get('artifacts',{})):raise Pending('Completed audio cache lacks required component/stem/loop evidence')
 for key,row in old['artifacts'].items():
  if key!=row['file']:raise Pending('Audio artifact name/record differs')
  source=(folder/row['file']).resolve()
  if not source.is_relative_to(folder.resolve())or sha(source)!=row['sha256']:raise Pending('Previously prepared audio changed or escaped owned folder')
 if old.get('mixWav')!=artifact(folder,'final-mix.wav'):raise Pending('Existing hash-bound mix descriptor differs from actual file')
 return old

def verified_audio_build(path):
 """Verify existing actual selected audio only; no worker, FFmpeg or writes."""
 path=Path(path).resolve()
 if not path.is_file():raise Pending('Actual accepted06 audio build is not available')
 old=read(path)
 ctx,recipe=prepare(old['rawVoiceAsr']['path'],old['rawNumericalLevelReview']['path'],old['acceptedComponentsReview']['path'])
 if recipe is None:raise Pending('Actual audio still lacks accepted component proof')
 folder=(DEST/recipe['fingerprint'][:24]).resolve()
 if path!=folder/'audio-build.json':raise Pending('Audio build is outside exact selected immutable output identity')
 result=reuse_audio(folder,recipe);voice=ctx['voice'];frames=voice['aggregateWav']['frames']
 if result['rawVoiceFingerprint']!=voice['fingerprint']or result['rawVoice']!=voice['aggregateWav']or result['canonicalTiming']!=voice['timing']or result['selectedComponentCount']!=len(voice['identity']['scenes']):raise Pending('Audio build does not bind exact current raw voice')
 mix=result['mixWav']
 if(mix['sampleRate'],mix['channels'],mix['frames'],mix['subtype'])!=(48000,2,frames*2,'FLOAT')or result['durationSeconds']!=frames/24000 or result['voiceOffsetSeconds']!=0 or result['insertedSamples']!=0 or result['trimmedSamples']!=0 or result['uniformMixGainDb']!=0:raise Pending('Audio rate/sample clock or unchanged voice gain contract differs')
 if result['rawVoiceAsr']!=ctx['asrPin']or result['rawNumericalLevelReview']!=ctx['levelPin']or result['acceptedComponentsReview']!=pin(old['acceptedComponentsReview']['path']):raise Pending('Actual audio acceptance/ASR/levels proof changed')
 lines=read(folder/'line-levels.json');expected_components=ctx['proposal']['identity']['components']
 if lines.get('schemaVersion')!='06-02-line-levels-v1'or lines.get('componentCount')!=len(expected_components)or lines.get('voiceFingerprint')!=voice['fingerprint']or lines.get('rawCanonical')!=voice['aggregateWav']or len(lines.get('components',[]))!=len(expected_components):raise Pending('Normalized component ledger does not bind current raw voice')
 for source,actual in zip(expected_components,lines['components']):
  if any(actual.get(k)!=v for k,v in source.items()):raise Pending('Normalized component ledger differs from accepted scalar proposal')
  name=source['sceneId']+'-normalized.wav'
  if actual['normalizedTake']!=name or name not in result['artifacts']or actual['normalizedTakeSHA256']!=result['artifacts'][name]['sha256']:raise Pending('Accepted normalized component file missing/changed')
 for name,expected_format in [('narration-component-normalized.wav',(24000,1,frames)),('narration-prepared-stem.wav',(48000,2,frames*2)),('narration-stem.wav',(48000,2,frames*2)),('music-stem.wav',(48000,2,frames*2))]:
  info=sf.info(folder/name)
  if(info.samplerate,info.channels,info.frames)!=expected_format:raise Pending('Actual component/stem clock differs')
 actual_plan=read(folder/'music-loop-plan.json')
 if result['musicLoopPlan']!=actual_plan:raise Pending('Actual music loop receipt differs')
 expected_plan=loop_plan(actual_plan['sourceFrames'],frames*2,48000)
 if any(actual_plan.get(k)!=v for k,v in expected_plan.items()):raise Pending('Music repeat/source-phase plan differs from approved1-second rule')
 if result['musicLoops']!=expected_plan['repeatCount']or result['musicContinuousExcerpt']!=(expected_plan['repeatCount']==0)or result['musicPlaybackRate']!=1:raise Pending('Music excerpt/repeat metadata is inaccurate')
 return result

def execute(asr_path,level_path,component_path):
 worker=runtime.SingleWorker(WORKER,is_alive=owned_audio_alive).acquire();worker.update(stage='CPU-audio',topicId='06.02')
 original_run=base.run;work=None
 try:
  ctx,recipe=prepare(asr_path,level_path,component_path)
  if recipe is None:raise Pending('Explicit acceptance of every exact selected component required before mix')
  folder=DEST/recipe['fingerprint'][:24]
  if folder.exists():
   return reuse_audio(folder,recipe)
  needed_disk=ctx['voice']['aggregateWav']['frames']*110+2*1024**3
  if shutil.disk_usage(TOPIC).free<needed_disk:raise Pending('Insufficient proportional C audio/reserve space; preserve original audio/media')
  needed_memory=ctx['voice']['aggregateWav']['frames']*128+2*364*48000*8+1024**3
  if runtime.psutil.virtual_memory().available<needed_memory:raise Pending('Insufficient available CPU memory for selected immutable audio/stems')
  work=DEST/('work-'+recipe['fingerprint'][:16]+'-'+uuid.uuid4().hex[:8]);work.mkdir(parents=True,exist_ok=False)
  save(work/'input-recipe.json',dict(**recipe,proposal=ctx['proposal'],voiceBinding=ctx['binding']))
  parts=[];records=[];rate=24000
  for source in ctx['proposal']['identity']['components']:
   samples,sr=sf.read(source['rawTake'],dtype='float32');matched,measure=base.match_paragraph(samples,sr,PROFILE)
   if sr!=rate or measure!=source['normalization']:raise Pending('Approved scalar proposal changed before normalization')
   name=source['sceneId']+'-normalized.wav';sf.write(work/name,matched,rate,subtype='FLOAT');parts.append(matched);records.append(dict(**source,normalizedTake=name,normalizedTakeSHA256=sha(work/name),normalizedTakeFloat32PcmSHA256=float_pcm_sha(matched),normalizationScope='one scalar for the complete approved semantic component'))
  normalized=np.concatenate(parts);voice=ctx['voice'];frames=voice['aggregateWav']['frames']
  if len(normalized)!=frames:raise Pending('Normalized voice length differs from canonical raw samples')
  norm=work/'narration-component-normalized.wav';sf.write(norm,normalized,rate,subtype='FLOAT')
  linelevels=dict(schemaVersion='06-02-line-levels-v1',componentCount=len(voice['identity']['scenes']),policy=PROFILE['policy'],voiceFingerprint=voice['fingerprint'],rawCanonical=voice['aggregateWav'],components=records,paragraphs=[dict(paragraph=n,sceneIds=[r['sceneId']for r in records if r['paragraph']==n],destinationSampleRange=[min(r['destinationSampleRange'][0]for r in records if r['paragraph']==n),max(r['destinationSampleRange'][1]for r in records if r['paragraph']==n)])for n in range(1,26)],joins=ctx['proposal']['identity']['joins'],rawRate=rate,frames=frames,durationSeconds=frames/rate,normalizedCopyOnly=True,originalRawFilesUnchanged=True,amplitudeOnlyScalarCopies=True,wordBoundariesShifted=False,voiceOffsetSeconds=0.,insertedSamples=0,trimmedSamples=0,voiceSpeed=1.,compressorUsed=False,voiceSideDuck=False,actualListening=False,automaticSpeechPass=False)
  save(work/'line-levels.json',linelevels)
  prepared=base.stereo_voice(normalized,rate);pp=work/'narration-prepared-stem.wav';sf.write(pp,prepared,48000,subtype='FLOAT')
  base.run=lambda command:tracked_run(worker,command)
  voice_gain,voice_levels=base.fixed_gain(prepared,base.loud(pp),PROFILE['voiceTargetLufs'],PROFILE['voiceSamplePeakCeilingDbfs']);stem=prepared*voice_gain
  native_info=json.loads(base.run([base.FF.with_name('ffprobe.exe'),'-v','error','-select_streams','a:0','-show_entries','stream=sample_rate,channels,duration','-of','json',base.MUSIC]).stdout)['streams'][0]
  data=base.run([base.FF,'-v','error','-i',base.MUSIC,'-map','0:a:0','-ar','48000','-ac','2','-f','f32le','pipe:1']).stdout
  music=np.frombuffer(data,dtype='<f4').reshape(-1,2).copy();ctx['musicRights']=dict(ctx['musicRights'],actualDecodedDurationPending=False,actualDecodedFrames=len(music),actualDecodedRate=48000,actualDecodedDurationSeconds=len(music)/48000,nativeContainerStream=native_info)
  if not np.isfinite(music).all():raise Pending('Nonfinite music decode')
  music_gain,nominal_music_levels=base.fixed_gain(music,base.loud(base.MUSIC),PROFILE['musicTargetLufs'],PROFILE['musicSamplePeakCeilingDbfs'])
  continuous_music,loop_proof=loop_music(music,len(stem),48000)
  save(work/'music-loop-plan.json',loop_proof)
  nominal_bed=base.music_bed(continuous_music,len(stem),48000,music_gain,base.duck_curve(stem,48000,PROFILE),PROFILE)
  compensation=music_headroom_compensation(voice_levels);bed,music_compensation=apply_music_compensation(nominal_bed,compensation)
  music_levels=effective_music_levels(nominal_music_levels,compensation)
  combined=stem+bed;overall=1.
  if base.db(np.max(np.abs(combined)))>PROFILE['mixSamplePeakCeilingDbfs']:raise Pending('Music-only mix exceeds sample-peak limit; preserve unchanged voice and hold without common-gain fallback')
  measured=None
  for attempt in range(2):
   trial=work/f'mix-measurement-{attempt+1}.wav';sf.write(trial,combined*overall,48000,subtype='FLOAT');measured=base.loud(trial)
   if float(measured['input_tp'])<=PROFILE['mixTruePeakMaximumDbtp']:break
   raise Pending('Music-only mix exceeds true-peak limit; preserve unchanged voice and hold without common-gain fallback')
  else:raise Pending('Actual true-peak blocker; preserve work, no compressor/limiter fallback')
  for name,values in [('narration-stem.wav',stem*overall),('music-stem.wav',bed*overall),('final-mix.wav',combined*overall)]:
   if not np.isfinite(values).all():raise Pending('Nonfinite processed audio')
   sf.write(work/name,values,48000,subtype='FLOAT')
  if prepare(asr_path,level_path,component_path)[1]['fingerprint']!=recipe['fingerprint']:raise Pending('Selected inputs changed during preparation; preserve work')
  names=[p.name for p in work.iterdir()if p.is_file()];artifacts={name:dict(file=name,sha256=sha(work/name))for name in names}
  mix=artifact(work,'final-mix.wav');mix['path']=str(folder/'final-mix.wav')
  result=dict(schemaVersion='06-02-audio-build-v1',topicId='06.02',status='audio-prepared-mixed-ASR-and-listening-pending',fingerprint=recipe['fingerprint'],output=str(folder),artifacts=artifacts,mixWav=mix,selectedComponentCount=len(voice['identity']['scenes']),rawVoice=voice['aggregateWav'],rawVoiceFingerprint=voice['fingerprint'],canonicalTiming=voice['timing'],normalizedVoiceFrames=frames,normalizedVoiceRate=rate,mixFrames=len(stem),mixRate=48000,durationSeconds=frames/rate,videoFrameTarget=dict(fps=60,totalFrames=math.ceil(frames*60/rate),noAudioTailPadding=True),pcmLineage=dict(normalized24kMonoFloat32SHA256=float_pcm_sha(normalized),prepared48kStereoFloat32SHA256=float_pcm_sha(prepared),finalVoice48kStereoFloat32SHA256=float_pcm_sha(stem),finalMusic48kStereoFloat32SHA256=float_pcm_sha(bed),finalMix48kStereoFloat32SHA256=float_pcm_sha(combined),voiceOffsetSamples=0,rawToPreparedSampleRatio=[2,1],voiceSpeed=1.),voiceGlobalGain=voice_levels,musicNominalGain=nominal_music_levels,musicGain=music_levels,musicOnlyCompensation=music_compensation,musicNativeStream=native_info,musicAttribution=base.LICENSE.read_text(encoding='utf-8').split('Credit for the description:\n\n')[-1].strip(),musicContinuousExcerpt=loop_proof['repeatCount']==0,musicPlaybackContinuous=True,musicLoops=loop_proof['repeatCount'],musicLoopPlan=loop_proof,musicRights=ctx['musicRights'],musicPlaybackRate=1.,musicSourceStartSeconds=0.,musicFadeSeconds=.45,musicSpeechDuckDb=4.,compressorUsed=False,voiceSideDuck=False,uniformMixGainDb=base.db(overall),measuredPcmMix=measured,originalRawFilesUnchanged=True,wordBoundariesShifted=False,voiceOffsetSeconds=0.,insertedSamples=0,trimmedSamples=0,historicalEngineAggregatePreserved=True,acceptedComponentsReview=pin(component_path),rawVoiceAsr=ctx['asrPin'],rawNumericalLevelReview=ctx['levelPin'],actualListening=False,automaticSpeechPass=False,finalMixedAsr='pending-exact-selected-mix-windows',encodedAacTruePeak='pending',encodedAlignedLevelReview='pending',finalMovieComplete=False,humanApproval=False)
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
