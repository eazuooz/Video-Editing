"""CPU V6 narration placement/mix preparation; original scene PCM is immutable.

The24k placed source is sample-exact. The48k stereo narration uses one constant
gain per scene and one common loudness/peak gain, with no voice ducking, fades,
time stretching or limiter. Added observation windows contain actual silence.
"""
from pathlib import Path
import argparse,hashlib,json,math,os,subprocess
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent
O=P/'production/local/revision-v6';V=O/'voice';A=O/'audio'
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
 args=['ffmpeg','-hide_banner','-nostdin','-i',str(path),'-map','0:a:0','-af','loudnorm=I=-16:TP=-1.8:LRA=11:print_format=json','-f','null','-']
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

def build(check_only=False):
 selected();timeline_file=H/'timeline.json';plan=read(timeline_file)
 assert plan['sceneCount']==41 and plan['lineCount']==250 and plan['beatCount']==106
 assert plan['fps']==60 and plan['originalPcmPreserved'] and plan['sourceSpeed']==1
 assert plan['plannedHoldFrames']==527*60
 assert plan.get('auxiliaryHoldFrames')==4*60 and plan.get('totalHoldFrames')==531*60
 inputs=dict(timelineSha256=sha(timeline_file),voiceAlignmentSha256=sha(V/'voice-alignment.json'),implementationSha256=sha(Path(__file__)))
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
  asr_file=V/'asr'/f'{scene["id"]}.json';asr=read(asr_file);assert asr['audio_sha256']==scene['rawVoiceSha256']
  mono=data[:,0].astype(np.float32)/32768.;speech=mask(len(mono),rate,asr['words'])
  assert speech.sum()>rate/2
  level=db(rms(mono[speech]));gain=-20.-level;assert abs(gain)<24
  windows=[]
  for start in range(0,len(mono)-round(.4*rate)+1,round(.1*rate)):
   end=start+round(.4*rate);active=speech[start:end]
   if active.sum()>=.15*rate:
    local=db(rms(mono[start:end][active]));windows.append(dict(rawStart=start/rate,rawEnd=end/rate,sourceDbfs=local,afterSceneGainDbfs=local+gain))
  rows.append(dict(scene=scene['id'],sourceFile=scene['rawVoiceFile'],sourceSha256=scene['rawVoiceSha256'],asrSha256=sha(asr_file),
   sourceSamples=len(data),sourceDecodedPcmInt16Sha256=hashlib.sha256(data.tobytes()).hexdigest(),speechRmsDbfs=level,constantSceneGainDb=gain,
   sourceSpeechWindowCount=len(windows),sourceSpeechWindows=windows,edgeFadeSeconds=0,voiceDucking=False,voiceLimiter=False,humanListening='pending'))
 if check_only:
  print('CPU input/placement contract valid;',len(rows),'scenes; no audio written');return
 A.mkdir(parents=True,exist_ok=True);total24=plan['totalFrames']*400;total48=plan['totalFrames']*800
 placed=A/'original-placed-24k.wav';fixed=A/'narration-fixed-gain-48k.wav'
 initialize(placed,24000,1,total24,'PCM_16');initialize(fixed,48000,2,total48,'FLOAT')
 with sf.SoundFile(placed,'r+') as original,sf.SoundFile(fixed,'r+') as processed:
  for scene,row in zip(plan['scenes'],rows):
   selected();data,rate=sf.read(R/scene['rawVoiceFile'],dtype='int16',always_2d=True)
   mono=data[:,0].astype(np.float32)/32768.
   # Resample the entire scene continuously before inserting pauses. Filters
   # never restart at sentence/quiet seams and never alter the archived PCM.
   stereo=np.repeat(resample_poly(mono,2,1)[:,None],2,axis=1)*10**(row['constantSceneGainDb']/20)
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
 stats=loudness(fixed,'voice-fixed-loudness')
 target_gain=-16.-float(stats['input_i']);peak_gain=-1.8-float(stats['input_tp']);global_gain=min(target_gain,peak_gain)
 stem=A/'narration-stem.wav';peak=0.;energy=0.;sample_count=0
 with sf.SoundFile(fixed) as src,sf.SoundFile(stem,'w',samplerate=48000,channels=2,subtype='FLOAT') as dst:
  for block in src.blocks(blocksize=48000*10,dtype='float32',always_2d=True):
   current_block=block*10**(global_gain/20);peak=max(peak,float(np.abs(current_block).max()));energy+=float(np.sum(current_block.astype(np.float64)**2));sample_count+=current_block.size;dst.write(current_block)
 for row in rows:row['constantGlobalGainDb']=global_gain;row['totalConstantGainDb']=row['constantSceneGainDb']+global_gain
 outputs=[dict(file=rel(f),sha256=sha(f)) for f in [placed,fixed,stem]]
 report=dict(schemaVersion=1,revision='article-flow-v6',inputs=inputs,outputs=outputs,scenes=rows,
  sampleRate=48000,channels=2,totalSamples=total48,totalFrames=plan['totalFrames'],seconds=plan['seconds'],
  primaryObservationHoldFrames=plan['plannedHoldFrames'],auxiliaryObservationHoldFrames=plan['auxiliaryHoldFrames'],totalObservationHoldFrames=plan['totalHoldFrames'],
  narrationFile=rel(stem),rawPlacedFile=rel(placed),noOriginalPcmMutation=True,everyOriginalSamplePreserved=True,
  fixedGainMeasurement=stats,globalGainDb=global_gain,loudnessTargetLufs=-16.,truePeakCeilingDbtp=-1.8,
  loudnessTargetPeakConstrained=peak_gain<target_gain,peakDbfs=db(peak),
  globalLevelPolicy='One per-scene constant speech RMS gain, then one whole-program constant gain; peak ceiling may prevent exact LUFS target. No limiter/fades/time stretch/voice duck.',
  separatelyAddedBgm=False,gameStem='pending root mixer handoff',sourceToStemContinuity='constant gain/math verified; contextual listening and final encoded comparison pending',
  humanWholeListening='pending',humanPaceListening='pending')
 save(current,report);print('Original PCM placed exactly;48k stereo constant-gain narration ready;',plan['seconds'],'seconds');return report

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--check-inputs',action='store_true');args=parser.parse_args();build(args.check_inputs)
