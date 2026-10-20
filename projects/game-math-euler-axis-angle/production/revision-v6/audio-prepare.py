"""CPU V6 narration placement/mix preparation; original scene PCM is immutable.

The24k placed source is sample-exact. The48k stereo narration uses one constant
gain per complete paragraph group in selected sustained-decay scenes, joins
only inside verified quiet, then one common loudness/peak gain. No word
compression, voice ducking/fade or stretching is used. An explicitly approved
transient-only lookahead limiter protects rare peaks after the fixed gains.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math,os,shutil,subprocess
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent
O=P/'production/local/revision-v6';V=O/'voice';A=O/'audio'
spec=importlib.util.spec_from_file_location('v6_narration_clip_gain',H/'voice-gain-plan.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def db(x):return 20*math.log10(max(float(x),1e-12))
def rms(x):return float(np.sqrt(np.mean(np.square(x,dtype=np.float64)))) if len(x) else 0.
def rel(p):return p.relative_to(R).as_posix()
def initialize(path,rate,channels,samples,subtype):
 with sf.SoundFile(path,'w',samplerate=rate,channels=channels,subtype=subtype) as f:
  zeros=np.zeros((min(rate*20,samples),channels),dtype=np.float32)
  while f.tell()<samples:f.write(zeros[:min(len(zeros),samples-f.tell())])
def loudness(path,name):
 args=['ffmpeg','-hide_banner','-nostdin','-threads','2','-filter_threads','2','-i',str(path),'-map','0:a:0','-af','loudnorm=I=-16:TP=-1.8:LRA=11:print_format=json','-f','null','-']
 run=subprocess.run(args,cwd=R,capture_output=True);(A/(name+'.log')).write_bytes(run.stderr)
 assert run.returncode==0,run.stderr.decode(errors='replace')[-2000:]
 text=run.stderr.decode(errors='replace');data=json.loads(text[text.rfind('{'):text.rfind('}')+1])
 assert math.isfinite(float(data['input_i']))
 return data
def selected():assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
def mask(size,rate,words):
 out=np.zeros(size,dtype=bool)
 for word in words:
  a,b=word['timestamp']
  if a is not None and b is not None and b>a:
   out[max(0,round(a*rate)):min(size,round(b*rate))]=True
 return out

def build(check_only=False,reuse_placement_from=None):
 selected();timeline_file=H/'timeline.json';plan=read(timeline_file)
 assert plan['sceneCount']==41 and plan['lineCount']==250 and plan['beatCount']==106
 assert plan['fps']==60 and plan['originalPcmPreserved'] and plan['sourceSpeed']==1
 assert plan['plannedHoldFrames']==527*60
 assert plan.get('auxiliaryHoldFrames')==4*60 and plan.get('totalHoldFrames')==531*60
 gain_file=V/'paragraph-gain-plan.json';gain_plan=read(gain_file);gain_by={s['id']:s for s in gain_plan['scenes']}
 assert gain_plan['inputs']['alignmentSha256']==sha(V/'voice-alignment.json') and gain_plan['inputs']['implementationSha256']==sha(H/'voice-gain-plan.py')
 inputs=dict(timelineSha256=sha(timeline_file),voiceAlignmentSha256=sha(V/'voice-alignment.json'),paragraphGainPlanSha256=sha(gain_file),gainImplementationSha256=sha(H/'voice-gain-plan.py'),implementationSha256=sha(Path(__file__)))
 current=A/'audio-build.json'
 if current.exists():
  old=read(current)
  if old.get('inputs')==inputs and all((R/f['file']).exists() and sha(R/f['file'])==f['sha256'] for f in old['outputs']):
   print('Exact successful narration placement reused; no audio rewritten');return old
  raise RuntimeError('Different existing V6 audio requires explicit preservation; no silent overwrite')
 rows=[]
 for scene in plan['scenes']:
  selected();raw=R/scene['rawVoiceFile'];assert sha(raw)==scene['rawVoiceSha256']
  data,rate=sf.read(raw,dtype='int16',always_2d=True);assert rate==24000 and data.shape[1]==1
  assert len(data)==scene['rawVoiceSamples'];segments=scene['voiceSegments'];at=0;destination_end=0
  for segment in segments:
   assert segment['sourceSampleStart']==at and segment['rate']==rate
   assert segment['destinationSampleStart']>=destination_end,'Placed source fragments must never overlap'
   destination_end=segment['destinationSampleStart']+segment['sourceSampleEnd']-segment['sourceSampleStart']
   at=segment['sourceSampleEnd']
  assert at==len(data),'Every original sample must appear once and in order'
  assert destination_end<=scene['frames']*400
  asr_file=R/scene['rawAsrFile'];asr=read(asr_file);assert sha(asr_file)==scene['rawAsrSha256'] and asr['audio_sha256']==scene['rawVoiceSha256']
  mono=data[:,0].astype(np.float32)/32768.;speech=mask(len(mono),rate,asr['words'])
  assert speech.sum()>rate/2
  level=db(rms(mono[speech]));gain=-20.-level;assert abs(gain)<24
  gain_row=gain_by[scene['id']];assert gain_row['sourceSha256']==scene['rawVoiceSha256']
  clip_curve=g.curve(gain_row,len(mono),rate);processed_preview=mono*clip_curve
  windows=[]
  for start in range(0,len(mono)-round(.4*rate)+1,round(.1*rate)):
   end=start+round(.4*rate);active=speech[start:end]
   if active.sum()>=.15*rate:
    local=db(rms(mono[start:end][active]));processed_level=db(rms(processed_preview[start:end][active]));windows.append(dict(rawStart=start/rate,rawEnd=end/rate,sourceDbfs=local,afterClipGainDbfs=processed_level,expectedClipGainDb=processed_level-local))
  rows.append(dict(scene=scene['id'],sourceFile=scene['rawVoiceFile'],sourceSha256=scene['rawVoiceSha256'],asrSha256=sha(asr_file),
   sourceSamples=len(data),sourceDecodedPcmInt16Sha256=hashlib.sha256(data.tobytes()).hexdigest(),speechRmsDbfs=level,baseSceneGainDb=gain,
   constantSceneGainDb=None if gain_row['selectedForParagraphGroupGain'] else gain_row['groups'][0]['constantGainDb'],clipGainPlan=gain_row,
   sourceSpeechWindowCount=len(windows),sourceSpeechWindows=windows,edgeFadeSeconds=0,voiceDucking=False,voiceLimiter='global-transient-only-stage;no-general-word-compression',humanListening='pending'))
 if check_only:
  print('CPU input/placement contract valid;',len(rows),'scenes; no audio written');return
 A.mkdir(parents=True,exist_ok=True);total24=plan['totalFrames']*400;total48=plan['totalFrames']*800
 placed=A/'original-placed-24k.wav';fixed=A/'narration-fixed-gain-48k.wav'
 reuse=None
 if reuse_placement_from is not None:
  archive=reuse_placement_from.resolve();assert archive.is_relative_to(O.resolve()) and archive!=A.resolve()
  prior_file=archive/'audio-build.json';prior=read(prior_file)
  assert prior['inputs']['timelineSha256']==inputs['timelineSha256'] and prior['inputs']['voiceAlignmentSha256']==inputs['voiceAlignmentSha256']
  assert len(prior['scenes'])==len(rows)==41 and prior['everyOriginalSamplePreserved']
  for current_row,prior_row in zip(rows,prior['scenes']):
   assert current_row['scene']==prior_row['scene'] and current_row['sourceSha256']==prior_row['sourceSha256']
   assert current_row['clipGainPlan']['groups']==prior_row['clipGainPlan']['groups'] and current_row['clipGainPlan']['boundaries']==prior_row['clipGainPlan']['boundaries']
   assert current_row['sourceDecodedPcmInt16Sha256']==prior_row['recoveredPlacedPcmInt16Sha256']
   current_row.update(recoveredPlacedPcmInt16Sha256=prior_row['recoveredPlacedPcmInt16Sha256'],everyOriginalSamplePreserved=True,placementStartFrame=prior_row['placementStartFrame'],placedDurationFrames=prior_row['placedDurationFrames'])
  for target in [placed,fixed]:
   record=next(x for x in prior['outputs'] if Path(x['file']).name==target.name);source=archive/target.name
   assert sha(source)==record['sha256']
   if not target.exists():shutil.copyfile(source,target)
   assert sha(target)==record['sha256']
  reuse=dict(receiptFile=rel(prior_file),receiptSha256=sha(prior_file),placementAndFixedGainFilesExactlyEqual=True,sourceSampleProofReused=True)
 else:
  initialize(placed,24000,1,total24,'PCM_16');initialize(fixed,48000,2,total48,'FLOAT')
 if reuse is None:
  with sf.SoundFile(placed,'r+') as original,sf.SoundFile(fixed,'r+') as processed:
   for scene,row in zip(plan['scenes'],rows):
    selected();data,rate=sf.read(R/scene['rawVoiceFile'],dtype='int16',always_2d=True)
    mono=data[:,0].astype(np.float32)/32768.
    # Resample the entire scene continuously before inserting pauses. Filters
    # never restart at sentence/quiet seams and never alter the archived PCM.
    resampled=resample_poly(mono,2,1);stereo=np.repeat((resampled*g.curve(row['clipGainPlan'],len(resampled),48000))[:,None],2,axis=1)
    recovered=hashlib.sha256();base24=scene['startFrame']*400;base48=scene['startFrame']*800
    for segment in scene['voiceSegments']:
     a,b,d=segment['sourceSampleStart'],segment['sourceSampleEnd'],segment['destinationSampleStart']
     original.seek(base24+d);original.write(data[a:b]);original.seek(base24+d)
     check=original.read(b-a,dtype='int16',always_2d=True);assert np.array_equal(check,data[a:b])
     recovered.update(check.tobytes());processed.seek(base48+d*2);processed.write(stereo[a*2:b*2])
    assert recovered.hexdigest()==row['sourceDecodedPcmInt16Sha256']
    prior_inserted=0
    for pause in scene['pauseInsertions']:
     original.seek(base24+pause['sourceSample']+prior_inserted)
     inserted=original.read(pause['insertSamples'],dtype='int16',always_2d=True)
     assert len(inserted)==pause['insertSamples'] and not np.any(inserted),'Only zero-valued samples may be inserted'
     prior_inserted+=pause['insertSamples']
    row['recoveredPlacedPcmInt16Sha256']=recovered.hexdigest();row['everyOriginalSamplePreserved']=True
    row['placementStartFrame']=scene['startFrame'];row['placedDurationFrames']=scene['frames']
 stats=prior['fixedGainMeasurement'] if reuse else loudness(fixed,'voice-fixed-loudness')
 global_gain=-16.-float(stats['input_i'])
 stem=A/'narration-stem.wav';limit=10**(-2.8/20)
 limiter_identity=dict(fixedGainSha256=sha(fixed),globalGainDb=global_gain,ceilingDbfs=-2.8,attackMs=5,releaseMs=50,automaticLevel=False,latencyCompensated=True)
 limiter_stage=A/'limiter-stage.json'
 command=['ffmpeg','-hide_banner','-nostdin','-threads','2','-filter_threads','2','-i',str(fixed),'-af',f'volume={global_gain:.12f}dB,alimiter=limit={limit:.12f}:attack=5:release=50:level=0:latency=1','-c:a','pcm_f32le',str(stem)]
 if limiter_stage.exists():
  previous=read(limiter_stage);assert previous['inputs']==limiter_identity and sha(stem)==previous['outputSha256'];print('Completed identical limiter stage reused; validating source alignment/levels only',flush=True)
 else:
  assert not stem.exists(),'Preserve an unreceipted processed output for explicit recovery review'
  run=subprocess.run(command,cwd=R,capture_output=True);(A/'voice-transient-limiter.log').write_bytes(run.stderr);assert run.returncode==0,run.stderr.decode(errors='replace')[-2000:]
  save(limiter_stage,dict(inputs=limiter_identity,outputSha256=sha(stem),ffmpegReturnCode=0))
 peak=0.;expanded_error=0.;numerical_expansion_violation=0.;limited_samples=0;minimum_gain=1.;maximum_gain=0.;zero_signal_changes=0;level_windows=[];position=0
 with sf.SoundFile(fixed) as source,sf.SoundFile(stem) as processed:
  assert source.frames==processed.frames==total48 and processed.samplerate==48000 and processed.channels==2
  for before,after in zip(source.blocks(blocksize=480000,dtype='float32',always_2d=True),processed.blocks(blocksize=480000,dtype='float32',always_2d=True)):
   expected=before*10**(global_gain/20);peak=max(peak,float(np.max(np.abs(after))));expanded_error=max(expanded_error,float(np.max(np.abs(after)-np.abs(expected))))
   numerical_expansion_violation=max(numerical_expansion_violation,float(np.max(np.abs(after)-np.abs(expected)*1.001-2e-6)))
   zero_signal_changes+=int(np.sum((expected[:,0]==0)&(after[:,0]!=0)))
   assert np.max(np.abs(after[:,0]-after[:,1]))<2e-6
   active=np.abs(expected[:,0])>1e-3
   if np.any(active):
    ratio=after[active,0]/expected[active,0]
    assert np.min(ratio)>=-2e-3 and np.max(ratio)<=1.003,'Limiter may attenuate, never flip polarity or expand narration'
    minimum_gain=min(minimum_gain,float(np.min(ratio)));maximum_gain=max(maximum_gain,float(np.max(ratio)))
   limited_samples+=int(np.sum(np.abs(after[:,0])<np.abs(expected[:,0])-2e-6))
   for start in range(0,len(before)-4800+1,4800):
    b=expected[start:start+4800,0];z=after[start:start+4800,0]
    if rms(b)>1e-3:level_windows.append(dict(globalStart=(position+start)/48000,globalEnd=(position+start+4800)/48000,preLimiterDbfs=db(rms(b)),postLimiterDbfs=db(rms(z)),limiterLevelChangeDb=db(rms(z))-db(rms(b))))
   position+=len(before)
 assert numerical_expansion_violation<=0 and zero_signal_changes==0,'Limiter must preserve alignment/silence and must not expand except sub0.01dB floating-control noise'
 limiter_stats=loudness(stem,'voice-limited-loudness')
 assert float(limiter_stats['input_tp'])<=-1.5 and -17<=float(limiter_stats['input_i'])<=-15,'Narration target or true peak requires contextual correction before mix'
 for row in rows:
  row['constantGlobalGainDb']=global_gain;row['totalConstantGainDb']=None if row['constantSceneGainDb'] is None else row['constantSceneGainDb']+global_gain
 outputs=[dict(file=rel(f),sha256=sha(f)) for f in [placed,fixed,stem]]
 report=dict(schemaVersion=1,revision='article-flow-v6',inputs=inputs,outputs=outputs,scenes=rows,
  sampleRate=48000,channels=2,totalSamples=total48,totalFrames=plan['totalFrames'],seconds=plan['seconds'],
  primaryObservationHoldFrames=plan['plannedHoldFrames'],auxiliaryObservationHoldFrames=plan['auxiliaryHoldFrames'],totalObservationHoldFrames=plan['totalHoldFrames'],
  narrationFile=rel(stem),rawPlacedFile=rel(placed),noOriginalPcmMutation=True,everyOriginalSamplePreserved=True,
  fixedGainMeasurement=stats,globalGainDb=global_gain,loudnessTargetLufs=-16.,truePeakCeilingDbtp=-1.8,
  loudnessTargetPeakConstrained=False,peakDbfs=db(peak),actualNarrationMeasurement=limiter_stats,placementReuse=reuse,
  transientLimiter=dict(enabled=True,approval='Root2026-10-20 permits only speech-safe transient peaks; no general word compression.',ceilingDbfs=-2.8,attackMs=5,releaseMs=50,automaticLevel=False,latencyCompensated=True,
   sourceAndOutputSamplesIdenticalCount=True,maximumAmplitudeExpansion=expanded_error,maximumSampleGain=maximum_gain,minimumSampleGain=minimum_gain,zeroInputBecameNonzeroSamples=zero_signal_changes,numericalExpansionRelativeTolerance=.001,
   attenuatedSampleCount=limited_samples,totalSamples=total48,local100msBeforeAfter=level_windows,processingStageReceiptSha256=sha(limiter_stage),humanListening='pending'),
  globalLevelPolicy='Constant complete-paragraph-group gain only for measured sustained-decay scenes; quiet-only gain joins, then one whole-program LUFS gain and transient-only lookahead peak safety.32take preserved with one scene gain. No general word compression, voice fades/stretch/duck.',
  paragraphGainPlanFile=rel(gain_file),paragraphGainPlanSha256=sha(gain_file),quietOnlyGainJoinCount=sum(len(r['clipGainPlan']['boundaries']) for r in rows),
  separatelyAddedBgm=False,gameStem='pending mixer',sourceToStemContinuity='Exact preserved placement, clip-gain/quiet-join map and transient-only limiter evidence recorded; contextual listening and encoded comparison pending',
  humanWholeListening='pending',humanPaceListening='pending')
 save(current,report);print('Original PCM placed exactly;48k stereo constant-gain narration ready;',plan['seconds'],'seconds');return report

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--check-inputs',action='store_true');parser.add_argument('--reuse-placement-from',type=Path);args=parser.parse_args();build(args.check_inputs,args.reuse_placement_from)
