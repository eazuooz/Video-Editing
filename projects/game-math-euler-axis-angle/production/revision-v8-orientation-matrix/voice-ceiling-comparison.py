"""CPU-only derived peak-ceiling experiment. Never selects or edits source PCM."""
from pathlib import Path
import hashlib,importlib.util,json,math,re,subprocess
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_ceiling_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
s=importlib.util.spec_from_file_location('v8_ceiling_word_view',H/'voice-analysis.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
def db(x):return 20*math.log10(max(float(x),1e-12))
def rms(x):return float(np.sqrt(np.mean(np.square(x,dtype=np.float64))))if len(x)else 0.
def runs(mask,rate):
 edges=np.diff(np.r_[False,mask,False].astype(np.int8));a=np.flatnonzero(edges==1);b=np.flatnonzero(edges==-1);lengths=(b-a)/rate
 return dict(samples=int(mask.sum()),seconds=float(mask.sum()/rate),longestSeconds=float(lengths.max())if len(lengths)else 0.,runs=len(a),
  durationBinCounts={str(lo)+'–'+str(hi)+'ms':int(np.sum((lengths*1000>lo)&(lengths*1000<=hi)))for lo,hi in [(0,.1),(.1,1),(1,5),(5,20),(20,50),(50,100),(100,1000000)]})
def measure(file,log):
 p=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-threads','2','-filter_threads','2','-i',str(file),'-af','loudnorm=I=-16:TP=-2.3:LRA=11:print_format=json','-f','null','-'],capture_output=True)
 log.write_bytes(p.stderr);assert p.returncode==0
 found=re.findall(r'\{\s*"input_i".*?\}',p.stderr.decode(errors='replace'),re.S);assert len(found)==1
 return json.loads(found[0])
def main():
 c.validate();source=c.read(c.O/'tts-current.json');head=c.read(c.O/'source-headroom.json');assert head['inputs']['sourceReceiptSha256']==c.sha(c.O/'tts-current.json')
 out=c.O/'diagnostics';out.mkdir(exist_ok=True);base=out/'target-global-gain.float.wav';limited=out/'derived-ceiling.float.wav'
 gain=-16-float(head['currentBodyInputLufs']);ceiling=-2.3;amplitude=10**(ceiling/20)
 fingerprint=dict(sourceReceiptSha256=c.sha(c.O/'tts-current.json'),sourceHeadroomSha256=c.sha(c.O/'source-headroom.json'),implementationSha256=c.sha(Path(__file__)),
  gainDb=gain,ceilingDbfs=ceiling,lookaheadMs=5,releaseMs=80,automaticLevel=False,limiterRate=192000,outputRate=48000)
 receipt=out/'ceiling-comparison-build.json';prior=c.read(receipt)if receipt.exists()else{}
 if prior.get('inputs')!=fingerprint or not base.exists()or not limited.exists()or c.sha(base)!=prior.get('baselineSha256')or c.sha(limited)!=prior.get('derivedSha256'):
  command=['ffmpeg','-y','-hide_banner','-nostdin','-threads','2','-filter_complex_threads','2','-f','concat','-safe','0','-i',str(c.O/'source-body.ffconcat'),
   '-filter_complex',f'[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume={gain:.12f}dB,asplit=2[base][pre];[pre]aresample=192000,alimiter=limit={amplitude:.12f}:attack=5:release=80:level=false:latency=true,aresample=48000[limited]',
   '-map','[base]','-c:a','pcm_f32le',str(base),'-map','[limited]','-c:a','pcm_f32le',str(limited)]
  result=subprocess.run(command,capture_output=True);(out/'ceiling-comparison-build.log').write_bytes(result.stderr);assert result.returncode==0
  c.save(receipt,dict(inputs=fingerprint,command=command,baseline=c.rel(base),baselineSha256=c.sha(base),derived=c.rel(limited),derivedSha256=c.sha(limited),
   sourceChanged=False,selectedForProduction=False,comparisonOnly=True))
 measurements=dict(baseline=measure(base,out/'baseline-loudness.log'),derived=measure(limited,out/'derived-loudness.log'))
 records=[];scene_offset=0;fs=48000;reductions=[];windows=[];combined={};longest={};total_samples=0
 for kind in ['sample0','sampleCeiling','oversampled0','oversampledCeiling']:combined[kind]=dict(seconds=0.,samples=0,runs=0,durationBinCounts={});longest[kind]=0.
 with sf.SoundFile(base)as a,sf.SoundFile(limited)as b:
  assert a.samplerate==b.samplerate==fs and a.channels==b.channels==2 and len(a)==len(b)
  for scene in source['scenes']:
   asr=c.read(c.R/scene['asrFile'])if scene.get('asrFile')else c.read(c.O/'asr'/(scene['id']+'.json'))
   words,_=v.monotonic_word_view(asr['words'])
   for line in scene['lines']:
    start=round((scene_offset+line['startSample'])*2);end=round((scene_offset+line['endSample'])*2);a.seek(start);b.seek(start)
    aa=a.read(end-start,dtype='float32');bb=b.read(end-start,dtype='float32');assert np.array_equal(aa[:,0],aa[:,1])and np.array_equal(bb[:,0],bb[:,1]);x=aa[:,0];y=bb[:,0]
    active=np.zeros(len(x),bool)
    for w in words:
     lo,hi=w['timestamp'];lo=round(lo*fs)-line['startSample']*2;hi=round(hi*fs)-line['startSample']*2
     if hi>0 and lo<len(x):active[max(0,lo):min(len(x),hi)]=True
    over=resample_poly(x,4,1);thresholds={'sample0':runs(abs(x)>1,fs),'sampleCeiling':runs(abs(x)>amplitude,fs),
     'oversampled0':runs(abs(over)>1,fs*4),'oversampledCeiling':runs(abs(over)>amplitude,fs*4)}
    for kind,data in thresholds.items():
     for key in ['seconds','samples','runs']:combined[kind][key]+=data[key]
     longest[kind]=max(longest[kind],data['longestSeconds'])
     for k,val in data['durationBinCounts'].items():combined[kind]['durationBinCounts'][k]=combined[kind]['durationBinCounts'].get(k,0)+val
    energy20=[]
    for lo in range(0,len(x)-960+1,960):
     hi=lo+960
     if active[lo:hi].sum()<288:continue
     before=db(rms(x[lo:hi]));after=db(rms(y[lo:hi]));energy20.append(dict(start=(start+lo)/fs,end=(start+hi)/fs,reductionDb=before-after,beforeDbfs=before,afterDbfs=after))
    local400=[]
    for lo in range(0,len(x)-19200+1,4800):
     hi=lo+19200;mask=active[lo:hi]
     if mask.sum()<7200:continue
     before=db(rms(x[lo:hi][mask]));after=db(rms(y[lo:hi][mask]));local400.append(dict(start=(start+lo)/fs,end=(start+hi)/fs,reductionDb=before-after,beforeDbfs=before,afterDbfs=after))
    record=dict(scene=scene['id'],line=line['line'],targetRange=[start/fs,end/fs],sourceTakeSha256=line['takeSha256'],
     baselineSamplePeakDbfs=db(abs(x).max()),oversampledBaselinePeakDbfs=db(abs(over).max()),derivedSamplePeakDbfs=db(abs(y).max()),
     exceedance=thresholds,firstSecondBaselineRmsDbfs=db(rms(x[:fs])),firstSecondDerivedRmsDbfs=db(rms(y[:fs])),
     bodyAfterFirstSecondBaselineRmsDbfs=db(rms(x[fs:][active[fs:]])),bodyAfterFirstSecondDerivedRmsDbfs=db(rms(y[fs:][active[fs:]])),
     maximum400msEnergyReductionDb=max([w['reductionDb']for w in local400],default=0),
     rms400ms=local400,energy20ms=energy20)
    records.append(record);reductions.extend(energy20);windows.extend(local400);total_samples+=len(x)
   scene_offset+=scene['samples'];print('Compared derived ceiling',scene['id'],flush=True)
  program_samples=len(a)
 for kind,data in combined.items():data['longestSeconds']=longest[kind];data['shareOfParagraphSeconds']=data['seconds']/(total_samples/fs)
 energy_summary={}
 for threshold in [.1,1,3,6]:
  selected=[w for w in reductions if w['reductionDb']>=threshold];groups=[]
  for w in selected:
   if groups and abs(w['start']-groups[-1]['end'])<.0001:groups[-1]['end']=w['end']
   else:groups.append(dict(start=w['start'],end=w['end']))
  energy_summary[str(threshold)]=dict(thresholdDb=threshold,quantized20msSeconds=len(selected)*.02,shareOfTimestampActive20msFrames=len(selected)/max(1,len(reductions)),
   longestConsecutive20msSeconds=max([g['end']-g['start']for g in groups],default=0),longestIntervals=sorted(groups,key=lambda g:g['end']-g['start'],reverse=True)[:8])
 result=dict(revision='orientation-matrix-v8',inputs=fingerprint,comparisonOnly=True,selectedForProduction=False,sourceChanged=False,
  files=c.read(receipt),measurements=measurements,parameters=dict(targetGlobalGainDb=gain,ceilingDbfs=ceiling,lookaheadMs=5,releaseMs=80,autoLevel=False,
   oversampling='4x48k→192k before linked-channel limiter, then48k'),durationSeconds=program_samples/fs,paragraphCount=len(records),
  exceedance=combined,energyReduction20ms=energy_summary,maximum400msSpeechEnergyReductionDb=max(w['reductionDb']for w in windows),
  worst400msWindows=sorted(windows,key=lambda w:w['reductionDb'],reverse=True)[:20],paragraphs=records,
  caveats=['input_* loudnorm values measure existing baseline/derived signals; output_* are discarded analysis output.',
   'Exceedance counts use complete paragraph sample ranges;4xresample_poly peak support differs slightly from FFmpeg whole-program resampling. Whole-program FFmpeg input_tp is separately measured.',
   '20ms/400ms RMS differences quantify output-energy change, not the internal limiter gain trace or a phonetic/loudness judgment.',
   'No source WAV/current receipt/ASR changed. No retake or final mix selected. Human listening and final moving pace remain pending.'],humanListening='pending')
 c.save(out/'ceiling-comparison.json',result)
 print(json.dumps(dict(baseline=measurements['baseline'],derived=measurements['derived'],exceedance=combined,energyReduction20ms=energy_summary),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
