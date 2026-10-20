"""Part1 source-preserving narration normalization; no inserted teaching pauses."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math,subprocess
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v7_audio_common',H/'audio-common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
sp2=importlib.util.spec_from_file_location('v7_audio_analysis',H/'voice-analysis.py');a=importlib.util.module_from_spec(sp2);sp2.loader.exec_module(a)
def db(x):return 20*math.log10(max(float(x),1e-12))
def rms(x):return float(np.sqrt(np.mean(np.square(x,dtype=np.float64)))) if len(x) else 0.
def initialize(path,rate,channels,samples,subtype):
 with sf.SoundFile(path,'w',samplerate=rate,channels=channels,subtype=subtype) as f:
  zeros=np.zeros((min(rate*10,samples),channels),dtype=np.float32)
  while f.tell()<samples:f.write(zeros[:min(len(zeros),samples-f.tell())])
def run(args,name):
 result=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y',*map(str,args)],cwd=c.R,capture_output=True)
 (c.O/(name+'.log')).write_bytes(result.stderr)
 assert result.returncode==0,result.stderr.decode(errors='replace')[-2400:]
 return result.stderr.decode(errors='replace')
def loudness(path,name):
 raw=run(['-threads','2','-filter_threads','2','-i',path,'-map','0:a:0','-af','loudnorm=I=-16:TP=-1.8:LRA=11:print_format=json','-f','null','-'],name)
 lo=raw.rfind('{');hi=raw.rfind('}')
 assert 0<=lo<hi
 return json.loads(raw[lo:hi+1])
def quiet_window(x,rate,low,high,reference):
 size=round(rate*.08);left=max(0,math.ceil(low*rate-1e-6));right=min(len(x),math.floor(high*rate+1e-6))
 if right-left<size:return None
 candidates=[]
 for lo in range(left,right-size+1,max(1,round(rate*.005))):
  w=x[lo:lo+size];level=rms(w);peak=float(np.max(np.abs(w)))
  if level<=min(.01,max(reference*.08,1e-6)) and peak<=min(.04,max(reference*.30,1e-5)):
   mid=lo+size//2;p=max(lo,mid-round(rate*.005));q=min(lo+size,mid+round(rate*.005));sample=p+int(np.argmin(np.abs(x[p:q])))
   candidates.append((level,abs(sample/rate-(low+high)/2),sample,peak,lo))
 if not candidates:return None
 level,_,sample,peak,lo=min(candidates)
 return dict(sampleOffset=sample,quietWindowSamples=[lo,lo+size],quietRms=level,quietPeak=peak,minimumQuietSeconds=.08)
def speech_mask(length,rate,words):
 mask=np.zeros(length,bool)
 for w in words:
  begin,end=w['timestamp']
  if begin is not None and end is not None and end>begin:mask[max(0,round(begin*rate)):min(length,round(end*rate))]=True
 return mask
def gain_plan(scene,alignment,spoken,cached,x,rate,normalize):
 mask=speech_mask(len(x),rate,cached['words']);paragraphs=[]
 for line in alignment['lines']:
  lo,hi=round(line['rawStart']*rate),round(line['rawEnd']*rate);active=x[lo:hi][mask[lo:hi]]
  assert len(active)>.15*rate,'Not enough timestamp-active evidence for paragraph gain'
  paragraphs.append(dict(line=line['line'],rawRange=[line['rawStart'],line['rawEnd']],sourceSpeechRmsDbfs=db(rms(active)),speechSamples=len(active)))
 span=max(p['sourceSpeechRmsDbfs'] for p in paragraphs)-min(p['sourceSpeechRmsDbfs'] for p in paragraphs)
 selected=span>=6 and len(paragraphs)>=3;words=[];prefix=''
 for raw in cached['words']:
  if not normalize(raw['text']):continue
  before=len(normalize(prefix));prefix+=' '+raw['text'];after=len(normalize(prefix))
  words.append(dict(word=raw,begin=before,end=after))
 text=normalize(prefix);boundaries=[];unavailable=[];reference=rms(x)
 if selected:
  for number in range(1,len(paragraphs)):
   suffix=normalize(spoken['lines'][number-1])[-12:];next_prefix=normalize(spoken['lines'][number])[:8];options=[]
   for j,w in enumerate(words[:-1]):
    terminal=w['word'];following=words[j+1]['word'];lo=terminal['timestamp'][1];hi=following['timestamp'][0]
    if lo is None or hi is None or hi<=lo or abs(lo-paragraphs[number-1]['rawRange'][1])>.35:continue
    if not text[:w['end']].endswith(suffix) or not text[w['end']:].startswith(next_prefix):continue
    quiet=quiet_window(x,rate,lo,hi,reference)
    if quiet:options.append((abs(lo-paragraphs[number-1]['rawRange'][1]),quiet,terminal,following))
   if options:
    _,quiet,terminal,following=min(options,key=lambda v:v[0])
    boundaries.append(dict(afterLine=number,**quiet,terminalWord=terminal,nextWord=following,completeParagraphSuffixAndNextPrefixMatched=True))
   else:unavailable.append(dict(afterLine=number,action='Keep same complete gain group; no fabricated quiet or word-internal gain boundary.'))
 starts=[0,*[v['sampleOffset'] for v in boundaries]];ends=[*[v['sampleOffset'] for v in boundaries],len(x)];groups=[];first=1
 for i,(lo,hi) in enumerate(zip(starts,ends)):
  last=boundaries[i]['afterLine'] if i<len(boundaries) else len(paragraphs)
  active=x[lo:hi][mask[lo:hi]];level=db(rms(active));gain=-20-level
  assert abs(gain)<24,'Extreme gain requires context review before normalization'
  groups.append(dict(firstLine=first,lastLine=last,sourceSampleStart=lo,sourceSampleEnd=hi,sourceSpeechRmsDbfs=level,constantGainDb=gain))
  first=last+1
 return dict(id=scene['id'],sourceFile=scene['rawVoiceFile'],sourceSha256=scene['rawVoiceSha256'],sourceSamples=len(x),sampleRate=rate,sourceParagraphs=paragraphs,sustainedParagraphSpanDb=span,selectedForParagraphGroupGain=selected and len(groups)>1,groups=groups,boundaries=boundaries,unavailableParagraphBoundaries=unavailable,sourcePcmChanged=False,timingChanged=False,humanContextualListening='pending')
def gain_curve(row,samples,rate=48000):
 out=np.full(samples,row['groups'][0]['constantGainDb'],np.float32)
 for boundary,group in zip(row['boundaries'],row['groups'][1:]):
  lo,hi=[round(v*rate/24000) for v in boundary['quietWindowSamples']]
  assert 0<=lo<hi<=samples
  before=float(out[lo]);after=group['constantGainDb']
  out[lo:hi]=np.linspace(before,after,hi-lo,dtype=np.float32);out[hi:]=after
 return np.power(np.float32(10),out/np.float32(20))
def build(timeline_file,check_only=False):
 plan=c.validate(preserve_pcm=True);timeline=c.read(timeline_file);alignment_file=c.O/'source-alignment.json';alignment=c.read(alignment_file)
 assert alignment['sceneCount']==21 and alignment['paragraphCount']==135 and not alignment['pending']
 direct_file=c.O/'source-direct-review.json';direct=c.read(direct_file)
 assert direct['allCurrent21TextsCompared'] and direct['unresolvedConfirmedContentErrors']==0,'Current complete raw transcripts must be directly reviewed first'
 spoken={s['id']:s for s in c.read(H/'voice-input.json')['scenes']};byid={s['id']:s for s in alignment['scenes']}
 assert [s['id'] for s in timeline['scenes']]==[f'v7-a{i:02}' for i in range(1,22)]
 assert timeline['introFrames']==120 and timeline['outroFrames']==600
 total_frames=timeline['totalFrames'];total24=total_frames*400;total48=total_frames*800;previous=120
 for scene in timeline['scenes']:
  assert scene['startFrame']==previous and scene['endFrame']==scene['startFrame']+scene['frames']
  assert scene['frames']==math.ceil(scene['rawVoiceSamples']/400) and scene['sampleRate']==24000
  assert 0<=scene['frames']*400-scene['rawVoiceSamples']<400
  previous=scene['endFrame']
 assert previous+600==total_frames
 inputs=dict(timelineFile=c.rel(timeline_file),timelineSha256=c.sha(timeline_file),alignmentSha256=c.sha(alignment_file),directContentReviewSha256=c.sha(direct_file),implementationSha256=c.sha(Path(__file__)),analysisImplementationSha256=c.sha(H/'voice-analysis.py'))
 receipt=c.O/'narration-build.json'
 if receipt.exists():
  old=c.read(receipt)
  if old['inputs']==inputs and all(c.sha(c.R/x['file'])==x['sha256'] for x in old['outputs']):print('Exact successful narration preparation reused');return old
  raise RuntimeError('Preserve differing prior audio preparation before a selected revision')
 if check_only:print('Current21PCM/direct-review/timeline inputs valid; no media written');return
 _,normalize=a.alignment_helpers();rows=[]
 for scene in timeline['scenes']:
  file=c.R/scene['rawVoiceFile'];assert c.sha(file)==scene['rawVoiceSha256']
  raw,rate=sf.read(file,dtype='int16');assert raw.ndim==1 and rate==24000 and len(raw)==scene['rawVoiceSamples']
  x=raw.astype(np.float32)/32768.;asr_file=c.R/byid[scene['id']]['asrFile'];cached=c.read(asr_file)
  assert c.sha(asr_file)==byid[scene['id']]['asrSha256'] and cached['audio_sha256']==scene['rawVoiceSha256']
  row=gain_plan(scene,byid[scene['id']],spoken[scene['id']],cached,x,rate,normalize)
  rows.append(row)
 c.save(c.O/'paragraph-gain-plan.json',dict(schemaVersion=1,part=1,inputs=inputs,scenes=rows,paragraphCount=135,sourceSamplesUnchanged=True,insertedObservationSilenceSamples=0,targetSpeechRmsDbfs=-20))
 placed=c.O/'source-placed-24k.wav';fixed=c.O/'narration-fixed-gain-48k.wav';stem=c.O/'narration-normalized-48k.wav'
 assert not any(p.exists() for p in [placed,fixed,stem]),'Unreceipted audio output must be inspected/preserved before retry'
 initialize(placed,24000,1,total24,'PCM_16');initialize(fixed,48000,2,total48,'FLOAT')
 equivalence=[]
 with sf.SoundFile(placed,'r+') as srcout,sf.SoundFile(fixed,'r+') as dstout:
  for scene,row in zip(timeline['scenes'],rows):
   raw,rate=sf.read(c.R/scene['rawVoiceFile'],dtype='int16');srcout.seek(scene['startFrame']*400);srcout.write(raw)
   resampled=resample_poly(raw.astype(np.float32)/32768.,2,1);processed=resampled*gain_curve(row,len(resampled));dstout.seek(scene['startFrame']*800);dstout.write(np.repeat(processed[:,None],2,axis=1))
 with sf.SoundFile(placed) as original,sf.SoundFile(fixed) as actual:
  for scene,row in zip(timeline['scenes'],rows):
   raw,_=sf.read(c.R/scene['rawVoiceFile'],dtype='int16');original.seek(scene['startFrame']*400);copied=original.read(len(raw),dtype='int16')
   assert np.array_equal(raw,copied),'Original PCM placement must be sample-exact'
   resampled=resample_poly(raw.astype(np.float32)/32768.,2,1);expected=resampled*gain_curve(row,len(resampled));actual.seek(scene['startFrame']*800);observed=actual.read(len(expected),dtype='float32',always_2d=True)
   maximum=float(np.max(abs(observed-expected[:,None])));assert maximum<2e-6
   equivalence.append(dict(id=scene['id'],sourceSha256=scene['rawVoiceSha256'],originalSamplesCompared=len(raw),everyOriginalSampleOnceInOrder=True,preLimiterMaximumError=maximum,framePaddingSamples24=scene['frames']*400-len(raw)))
 stats=loudness(fixed,'narration-fixed-loudness');global_gain=-16-float(stats['input_i'])
 assert abs(global_gain)<12
 required=float(stats['input_tp'])+global_gain>-1.8
 limiter=dict(enabled=required,ceilingDbfs=-2.8,attackMs=5,releaseMs=50,automaticLevel=False,latencyCompensated=True,reason='Measured fixed-gain+LUFS normalization transient peak exceeds speech headroom' if required else 'No transient limiter needed at measured gain')
 if required:
  ceiling=10**(-2.8/20)
  run(['-threads','2','-filter_threads','2','-i',fixed,'-af',f'volume={global_gain:.12f}dB,alimiter=limit={ceiling:.12f}:attack=5:release=50:level=0:latency=1','-c:a','pcm_f32le',stem],'narration-transient-safety')
 else:
  with sf.SoundFile(fixed) as inp,sf.SoundFile(stem,'w',samplerate=48000,channels=2,subtype='FLOAT') as out:
   for block in inp.blocks(blocksize=480000,dtype='float32',always_2d=True):out.write(block*10**(global_gain/20))
 peak=0.;expanded=0.;zero_changes=0;attenuated=0;position=0;windows=[];factor=10**(global_gain/20)
 with sf.SoundFile(fixed) as inp,sf.SoundFile(stem) as out:
  assert inp.frames==out.frames==total48 and out.samplerate==48000 and out.channels==2
  for before,after in zip(inp.blocks(blocksize=480000,dtype='float32',always_2d=True),out.blocks(blocksize=480000,dtype='float32',always_2d=True)):
   expected=before*factor;peak=max(peak,float(np.max(abs(after))));expanded=max(expanded,float(np.max(abs(after)-abs(expected)*(1+.001))))
   zero_changes+=int(np.sum((expected==0)&(after!=0)));attenuated+=int(np.sum(abs(after[:,0])<abs(expected[:,0])-2e-6))
   for lo in range(0,len(before)-4800+1,4800):
    x=expected[lo:lo+4800,0];y=after[lo:lo+4800,0]
    if rms(x)>1e-3:windows.append(dict(start=(position+lo)/48000,end=(position+lo+4800)/48000,beforeDbfs=db(rms(x)),afterDbfs=db(rms(y)),changeDb=db(rms(y))-db(rms(x))))
   position+=len(before)
 assert zero_changes==0 and expanded<=0,'Unexpected source alignment/silence/amplitude expansion'
 measured=loudness(stem,'narration-normalized-loudness')
 assert float(measured['input_tp'])<=-1.5 and -17<=float(measured['input_i'])<=-15
 limiter.update(attenuatedMonoSampleCount=attenuated,totalSamples=total48,maximumExpansionAboveTolerance=expanded,zeroInputBecameNonzeroSamples=zero_changes,local100msBeforeAfter=windows,contextualListening='pending')
 report=dict(schemaVersion=1,part=1,revision='v7-part1',inputs=inputs,outputs=[dict(file=c.rel(f),sha256=c.sha(f)) for f in [placed,fixed,stem]],narrationFile=c.rel(stem),sampleRate=48000,channels=2,totalFrames=total_frames,totalSamples=total48,seconds=total_frames/60,scenes=rows,originalPlacementAndFixedGainProof=equivalence,everyOriginalSampleOnceInOrder=True,noSourcePcmMutation=True,insertedTeachingPauseSamples=0,onlySilence='Original natural quiet, original120/600branding/member regions and subframe tail padding.',voiceSpeed=1,sourceToStemGain='Constant complete-group gains;80ms verified quiet-only transitions; one common LUFS gain; measured-needed transient-only safety, no voice ducking/fade/time stretch.',fixedGainMeasurement=stats,constantGlobalGainDb=global_gain,transientLimiter=limiter,actualNarrationMeasurement=measured,finalEncodedMix='pending game timing/mix and once-only encoded-ASR/continuity review',humanWholeListening='pending')
 c.save(receipt,report);print('Prepared actual narration:',report['seconds'],'seconds;',measured['input_i'],'LUFS;',measured['input_tp'],'dBTP; original PCM preserved')
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--timeline',type=Path,default=H/'timeline.json');p.add_argument('--check-inputs',action='store_true');args=p.parse_args();build(args.timeline.resolve(),args.check_inputs)
